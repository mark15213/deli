# 算子化 Pipeline 设计方案

## 一、现状问题分析

当前系统的核心问题：

1. **硬编码编排**：`runner_service.py` 的 `process_new_source()` 用 400 行过程式代码硬编码了 summary → reading_notes → study_quiz → figure_association 的执行顺序，每加一个处理步骤都要改这个函数
2. **处理步骤定义不完整**：当前只有 prompt 配置，缺少输入/输出类型声明，无法做类型校验和自动连线
3. **非 LLM 步骤无法表达**：PDF 文本提取、图片提取、图片优化等"工具型"操作散落在 runner_service 里，无法复用
4. **无 DAG 支持**：当前是严格串行，reading_notes 和 study_quiz 其实可以并行（都只依赖 text），但做不到
5. **Registry 是 if-else 工厂**：当前的注册机制是一个 switch-case，不可扩展

## 二、核心设计：Operator + Pipeline

### 2.1 Operator（算子）

将所有处理步骤统一抽象为 Operator。一个 Operator 就是一个有明确输入/输出 schema 的处理单元。

```
┌─────────────────────────────────┐
│           Operator              │
├─────────────────────────────────┤
│ key: str                        │  唯一标识
│ name: str                       │  显示名
│ kind: "llm" | "tool"           │  算子类型
│ input_ports: [Port]             │  输入端口定义
│ output_ports: [Port]            │  输出端口定义
│ config: OperatorConfig          │  算子配置
└─────────────────────────────────┘
```

两种算子类型：

| Kind | 说明 | 示例 |
|------|------|------|
| `llm` | 调用 LLM，有 prompt 模板 | summary, reading_notes, study_quiz, figure_association |
| `tool` | 纯代码逻辑，无 LLM 调用 | pdf_extract_text, pdf_extract_figures, optimize_images, save_cards |

### 2.2 Port（端口）

每个算子有明确的输入/输出端口，端口有类型：

```python
class PortType(str, Enum):
    TEXT = "text"           # 纯文本 str
    JSON = "json"           # 结构化 dict/list
    IMAGES = "images"       # List[bytes]
    PDF_BYTES = "pdf_bytes" # bytes
    CARDS = "cards"         # List[CardData]

class Port(BaseModel):
    key: str                # 端口名，如 "text", "notes", "figures"
    type: PortType
    description: str
    required: bool = True
```

连线规则：只有类型兼容的端口才能连接。前端画布据此做校验。

### 2.3 Pipeline（管线）

Pipeline 是一个 DAG（有向无环图），由 nodes + edges 组成：

```python
class PipelineNode(BaseModel):
    id: str                          # 实例 ID（画布上的节点）
    operator_key: str                # 引用哪个 Operator
    config_overrides: dict = {}      # 覆盖算子默认配置（如 temperature）
    position: dict = {"x": 0, "y": 0}  # 画布坐标（纯前端用）

class PipelineEdge(BaseModel):
    id: str
    source_node: str                 # 源节点 ID
    source_port: str                 # 源端口 key
    target_node: str                 # 目标节点 ID
    target_port: str                 # 目标端口 key

class Pipeline(BaseModel):
    id: str
    name: str
    description: str = ""
    nodes: list[PipelineNode]
    edges: list[PipelineEdge]
    created_at: datetime
    updated_at: datetime
```

### 2.4 示例：当前论文处理流程用 Pipeline 表达

```
                    ┌──────────────┐
                    │  pdf_fetch   │ (tool)
                    │              │
                    │ out: text    │──────────┬──────────────┐
                    │ out: pdf_bytes│─────┐   │              │
                    └──────────────┘     │   │              │
                                         │   │              │
                    ┌──────────────┐     │   │    ┌─────────▼────┐
                    │extract_figures│◄────┘   │    │  summary     │
                    │  (tool)      │         │    │  (llm)       │
                    │ out: images  │──┐      │    └──────────────┘
                    └──────────────┘  │      │
                                      │      │
                    ┌──────────────┐  │   ┌──▼─────────────┐
                    │optimize_imgs │◄─┘   │ reading_notes   │
                    │  (tool)      │      │ (llm)           │
                    │ out: images  │──┐   │ out: json       │──┐
                    └──────────────┘  │   └─────────────────┘  │
                                      │                         │
                                      │   ┌─────────────────┐  │
                                      └──►│figure_association│◄─┘
                                          │ (llm)           │
                                          └────────┬────────┘
                                                   │
                                          ┌────────▼────────┐
                                          │  save_cards     │
                                          │  (tool)         │
                                          └─────────────────┘

                              ┌──────────────────┐
                    text ────►│  study_quiz      │
                              │  (llm)           │
                              │  out: json       │──► save_cards (tool)
                              └──────────────────┘
```

注意 `reading_notes` 和 `study_quiz` 可以并行执行（都只依赖 text）。

## 三、后端实现

### 3.1 新增数据模型

```python
# models.py 新增

class PipelineTemplate(Base):
    """可复用的 Pipeline 模板"""
    __tablename__ = "pipeline_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]]  # NULL = 系统内置
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, default="")
    definition: Mapped[dict] = mapped_column(JSONB)  # Pipeline JSON（nodes + edges）
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
```

### 3.2 Operator 基类与注册

```
backend/app/operators/
├── __init__.py
├── base.py              # Operator 抽象基类 + Port/PortType 定义
├── registry.py          # 算子注册表（装饰器自动注册）
├── engine.py            # PipelineEngine（DAG 执行引擎）
├── llm/
│   ├── __init__.py
│   ├── base.py          # LLMOperator 基类（prompt 渲染 + LLM 调用 + JSON 解析）
│   ├── summary.py
│   ├── reading_notes.py
│   ├── study_quiz.py
│   └── figure_association.py
└── tool/
    ├── __init__.py
    ├── loader.py            # ToolOperator 通用类 + YAML manifest 加载器
    ├── manifests/           # 声明式 manifest（每个 tool 一个 YAML）
    │   ├── pdf_fetch.yaml
    │   ├── extract_figures.yaml
    │   ├── optimize_images.yaml
    │   └── save_cards.yaml
    └── handlers/            # 纯函数 handler（每个 tool 一个 .py）
        ├── __init__.py
        ├── pdf_fetch.py
        ├── extract_figures.py
        ├── optimize_images.py
        └── save_cards.py
```

#### Operator 基类

```python
# base.py
from abc import ABC, abstractmethod
from enum import Enum
from pydantic import BaseModel
from typing import Any

class PortType(str, Enum):
    TEXT = "text"
    JSON = "json"
    IMAGES = "images"
    PDF_BYTES = "pdf_bytes"
    CARDS = "cards"

class Port(BaseModel):
    key: str
    type: PortType
    description: str
    required: bool = True

class RunContext(BaseModel):
    """执行上下文，传递 DB session、source_id 等"""
    db: Any  # AsyncSession
    source_id: str
    user_id: str
    source_material_id: str | None = None

class OperatorBase(ABC):
    """所有算子的基类"""
    key: str
    name: str
    kind: str  # "llm" | "tool"
    description: str = ""
    input_ports: list[Port]
    output_ports: list[Port]

    @abstractmethod
    async def execute(self, inputs: dict[str, Any], context: RunContext) -> dict[str, Any]:
        """
        执行算子。
        inputs:  {port_key: value}  按输入端口名传入数据
        returns: {port_key: value}  按输出端口名返回数据
        """
        ...

    def get_manifest(self) -> dict:
        """返回算子元信息，供前端渲染节点面板"""
        return {
            "key": self.key,
            "name": self.name,
            "kind": self.kind,
            "description": self.description,
            "input_ports": [p.model_dump() for p in self.input_ports],
            "output_ports": [p.model_dump() for p in self.output_ports],
        }
```

#### LLM 算子基类

```python
# llm/base.py
class LLMOperator(OperatorBase):
    """LLM 算子基类，自动处理 prompt 渲染 + LLM 调用 + JSON 解析"""
    kind = "llm"
    prompt_file: str          # YAML 文件名（复用现有 prompts/ 目录）
    output_schema: dict | None = None

    async def execute(self, inputs, context):
        config = load_prompt_config(self.prompt_file)
        messages = self._render_messages(config, inputs)
        response = await llm_client.chat(
            messages=messages,
            output_schema=self.output_schema,
        )
        return self._map_output(response.content)

    def _render_messages(self, config, inputs) -> list[dict]:
        """将 prompt 模板 + inputs 渲染为 LLM messages"""
        system_prompt = config["system_prompt"]
        user_prompt = config["user_prompt_template"].format(**inputs)
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    @abstractmethod
    def _map_output(self, content) -> dict[str, Any]:
        """子类实现：将 LLM 输出映射到输出端口"""
        ...
```

#### Tool 算子设计

Tool 算子参考 skill 的设计模式，采用声明式 manifest + handler 的方式。每个 tool 通过一个 YAML manifest 声明自身的元信息（名称、描述、输入/输出端口），再关联一个纯函数 handler 实现具体逻辑。这样 tool 的定义和实现分离，新增 tool 只需要写一个 YAML + 一个 handler 函数，无需继承基类。

```yaml
# tool/manifests/pdf_fetch.yaml
key: pdf_fetch
name: Fetch PDF
description: Download PDF and extract text content
input_ports:
  - key: url
    type: text
    description: PDF URL
output_ports:
  - key: text
    type: text
    description: Extracted text
  - key: pdf_bytes
    type: pdf_bytes
    description: Raw PDF bytes
handler: tool.handlers.pdf_fetch  # 指向 handler 函数的模块路径
```

```python
# tool/handlers/pdf_fetch.py
async def handle(inputs: dict, context: RunContext) -> dict:
    """纯函数 handler，无需继承任何基类"""
    url = inputs["url"]
    pdf_bytes = await download_pdf(url)
    text = extract_text_from_pdf(pdf_bytes)
    return {"text": text, "pdf_bytes": pdf_bytes}
```

```python
# tool/loader.py
class ToolOperator(OperatorBase):
    """通用 Tool 算子，从 YAML manifest 加载元信息，动态绑定 handler"""
    kind = "tool"

    def __init__(self, manifest: dict, handler_fn: Callable):
        self.key = manifest["key"]
        self.name = manifest["name"]
        self.description = manifest.get("description", "")
        self.input_ports = [Port(**p) for p in manifest["input_ports"]]
        self.output_ports = [Port(**p) for p in manifest["output_ports"]]
        self._handler = handler_fn

    async def execute(self, inputs, context):
        return await self._handler(inputs, context)

def load_tool_operators() -> list[ToolOperator]:
    """扫描 manifests/ 目录，加载所有 tool 算子"""
    operators = []
    for yaml_path in Path("tool/manifests").glob("*.yaml"):
        manifest = yaml.safe_load(yaml_path.read_text())
        handler_fn = import_handler(manifest["handler"])
        operators.append(ToolOperator(manifest, handler_fn))
    return operators
```

#### 算子注册表

```python
# registry.py
_REGISTRY: dict[str, type[OperatorBase]] = {}

def register_operator(cls):
    """装饰器：自动注册算子"""
    _REGISTRY[cls.key] = cls
    return cls

def get_operator(key: str) -> OperatorBase:
    return _REGISTRY[key]()

def get_all_manifests() -> list[dict]:
    return [cls().get_manifest() for cls in _REGISTRY.values()]
```

### 3.3 Pipeline Engine（DAG 执行引擎）

```python
# engine.py
class PipelineEngine:
    """拓扑排序 + 并行执行 DAG"""

    async def run(self, pipeline: Pipeline, initial_inputs: dict, context: RunContext):
        graph = self._build_graph(pipeline)
        levels = self._topological_levels(graph)  # 分层，同层可并行

        node_outputs: dict[str, dict] = {}
        node_outputs["__input__"] = initial_inputs

        for level in levels:
            # 同一层的节点并行执行
            tasks = []
            for node in level:
                inputs = self._gather_inputs(node, pipeline.edges, node_outputs)
                operator = get_operator(node.operator_key)
                tasks.append(self._run_node(node, operator, inputs, context))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for node, result in zip(level, results):
                if isinstance(result, Exception):
                    await self._handle_failure(node, result, context)
                else:
                    node_outputs[node.id] = result

        return node_outputs

    def _topological_levels(self, graph) -> list[list[PipelineNode]]:
        """Kahn's algorithm 变体，返回分层结果（同层可并行）"""
        ...

    def _gather_inputs(self, node, edges, outputs) -> dict:
        """根据 edges 从上游节点的 outputs 中收集当前节点的 inputs"""
        inputs = {}
        for edge in edges:
            if edge.target_node == node.id:
                source_data = outputs[edge.source_node][edge.source_port]
                inputs[edge.target_port] = source_data
        return inputs

    async def _run_node(self, node, operator, inputs, context):
        """执行单个节点，带日志记录"""
        await log_event(context, "operator_started", operator.key)
        start = time.time()
        try:
            result = await operator.execute(inputs, context)
            duration = int((time.time() - start) * 1000)
            await log_event(context, "operator_completed", operator.key, duration_ms=duration)
            return result
        except Exception as e:
            duration = int((time.time() - start) * 1000)
            await log_event(context, "operator_failed", operator.key, duration_ms=duration, error=str(e))
            raise
```

### 3.4 新增 API

```
GET  /api/v1/operators              → 返回所有可用算子的 manifest（前端渲染算子面板）
GET  /api/v1/pipelines              → 列出用户的 pipeline 模板
POST /api/v1/pipelines              → 创建/保存 pipeline（JSON body = Pipeline 定义）
GET  /api/v1/pipelines/{id}         → 获取 pipeline 详情
PUT  /api/v1/pipelines/{id}         → 更新 pipeline
POST /api/v1/pipelines/{id}/run     → 执行 pipeline（传入 source_id）
GET  /api/v1/pipelines/presets      → 获取系统内置 pipeline 模板
```

### 3.5 向后兼容

- 现有 `process_new_source()` 改为：加载名为 `"paper_default"` 的系统内置 Pipeline 模板，交给 PipelineEngine 执行
- 现有 YAML prompt 文件原样保留，被 LLMOperator 引用
- 现有 SourceLog 机制保留，PipelineEngine 在每个节点执行前后写 log

## 四、前端：Xyflow 画布

### 4.1 技术选型

**Xyflow（React Flow v12）**：MIT 协议，35K+ stars，4.6M 周下载量，完美适配 Next.js + Tailwind。

```bash
npm install @xyflow/react
```

### 4.2 页面结构

```
/pipelines                    → Pipeline 列表页
/pipelines/new                → 新建 Pipeline（画布）
/pipelines/{id}/edit          → 编辑 Pipeline（画布）

画布页面布局：
┌─────────────────────────────────────────────────┐
│ Toolbar: [保存] [运行] [预设模板▼]               │
├──────────┬──────────────────────────────────────┤
│ 算子面板  │                                      │
│          │         Xyflow 画布                   │
│ ┌──────┐ │                                      │
│ │ LLM  │ │    从左侧拖拽算子到画布               │
│ │算子们 │ │    连线端口形成 DAG                   │
│ ├──────┤ │    点击节点编辑配置                    │
│ │ Tool │ │                                      │
│ │算子们 │ │                                      │
│ └──────┘ │                                      │
├──────────┴──────────────────────────────────────┤
│ 底部: 执行日志 / 节点状态                         │
└─────────────────────────────────────────────────┘
```

### 4.3 核心组件

```
web/src/app/pipelines/
├── page.tsx                      # Pipeline 列表
├── [id]/edit/page.tsx            # 画布编辑页
└── components/
    ├── PipelineCanvas.tsx         # Xyflow 画布主组件
    ├── OperatorPanel.tsx          # 左侧算子面板（从 GET /operators 获取）
    ├── OperatorNode.tsx           # 自定义 Xyflow 节点（显示端口、名称、kind 图标）
    ├── PortHandle.tsx             # 自定义端口手柄（按 PortType 着色）
    ├── NodeConfigDrawer.tsx       # 点击节点弹出的配置抽屉（编辑 config_overrides）
    └── ExecutionOverlay.tsx       # 运行时状态覆盖层（节点变绿/红/转圈）
```

### 4.4 端口类型颜色编码

| PortType | 颜色 | 含义 |
|----------|------|------|
| TEXT | 蓝色 `#3b82f6` | 文本流 |
| JSON | 紫色 `#8b5cf6` | 结构化数据 |
| IMAGES | 绿色 `#22c55e` | 图片列表 |
| PDF_BYTES | 橙色 `#f97316` | PDF 原始数据 |
| CARDS | 黄色 `#eab308` | 卡片数据 |

连线时只有类型相同的端口可以连接，提供即时视觉反馈。

### 4.5 序列化格式

画布状态直接序列化为 Pipeline JSON 存入后端：

```json
{
  "name": "Paper Processing",
  "nodes": [
    {
      "id": "node-1",
      "operator_key": "pdf_fetch",
      "config_overrides": {},
      "position": {"x": 100, "y": 200}
    },
    {
      "id": "node-2",
      "operator_key": "summary",
      "config_overrides": {"temperature": 0.5},
      "position": {"x": 400, "y": 100}
    }
  ],
  "edges": [
    {
      "id": "edge-1",
      "source_node": "node-1",
      "source_port": "text",
      "target_node": "node-2",
      "target_port": "text"
    }
  ]
}
```

## 五、内置算子清单（v1）

### LLM 算子

| Key | 输入端口 | 输出端口 | 说明 |
|-----|---------|---------|------|
| `summary` | text:TEXT | summary:TEXT | TL;DR 摘要 |
| `reading_notes` | text:TEXT | notes:JSON | 9 部分结构化笔记 |
| `study_quiz` | text:TEXT | flashcards:JSON | 闪卡生成 |
| `figure_association` | text:TEXT, images:IMAGES | associations:JSON | 图文关联 |
| `profiler` | text:TEXT | suggestions:JSON | 内容分析建议 |

### Tool 算子

| Key | 输入端口 | 输出端口 | 说明 |
|-----|---------|---------|------|
| `pdf_fetch` | url:TEXT | text:TEXT, pdf_bytes:PDF_BYTES | 下载 PDF 并提取文本 |
| `extract_figures` | pdf_bytes:PDF_BYTES | images:IMAGES | 从 PDF 提取图片 |
| `optimize_images` | images:IMAGES | images:IMAGES | 压缩图片供 LLM 使用 |
| `save_cards` | json:JSON, card_type:TEXT | cards:CARDS | 将 JSON 结果存为 Card 记录 |

## 六、实施路径

### Phase 1：后端算子框架（不改变现有行为）
1. 创建 `operators/` 目录结构
2. 实现 `OperatorBase`、`Port`、`PortType`、`RunContext`
3. 实现 `LLMOperator` 基类（prompt 渲染 + LLM 调用 + JSON 解析）
4. 将现有 5 个处理步骤迁移为 LLMOperator 子类
5. 实现 Tool manifest + handler 机制，将 pdf_fetch、extract_figures 等提取为声明式 ToolOperator
6. 实现 Registry（装饰器自动注册 LLM 算子 + manifest 扫描注册 Tool 算子）
7. 实现 PipelineEngine（DAG 拓扑排序 + 并行执行）
8. 创建 `paper_default` 内置 Pipeline 模板
9. 改造 `process_new_source()` 为调用 PipelineEngine
10. 验证：现有论文处理流程行为不变

### Phase 2：Pipeline 持久化 + API
1. 新增 `pipeline_templates` 表 + Alembic migration
2. 实现 Pipeline CRUD API
3. 实现 Pipeline 执行 API（含实时日志推送）
4. Seed 系统内置模板

### Phase 3：前端画布
1. `npm install @xyflow/react`
2. 实现 PipelineCanvas + OperatorNode + PortHandle
3. 实现 OperatorPanel（拖拽）
4. 实现 NodeConfigDrawer
5. 实现保存/加载 Pipeline
6. 实现执行状态可视化（WebSocket 或 SSE 推送节点状态）

### Phase 4：增强（后续）
1. 支持用户自定义 LLM 算子（在前端编辑 prompt + output_schema）
2. 支持用户自定义 Tool 算子（上传 YAML manifest + handler）
3. 支持条件分支算子（if/else）
4. Pipeline 版本管理
5. 执行历史与对比
