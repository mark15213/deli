# LLM 调用监控系统实现方案

## 目标
精准监控每个 LLM 调用的执行情况，包括输入输出、token 消耗、耗时、成本等，支持两个粒度：
1. **细粒度**：每次 `chat.completions.create` API 调用
2. **粗粒度**：每个 Lens 执行的汇总统计

输出方式：结构化日志（JSON 格式），方便后续用日志分析工具处理

## 现状分析

### 当前架构
- **RunnerService** (`backend/app/services/runner_service.py`):
  - 第 162 行：`chat.completions.create` 调用
  - 第 225-232 行：已有简单的日志输出（模型名、响应内容前 200 字符）
  - 第 227-229 行：已记录耗时 `duration_ms`
  - 第 246 行：usage 字段只存了 `duration_ms`，**没有 token 信息**

- **GeneratorService** (`backend/app/services/generator_service.py`):
  - 第 133 行：另一个 LLM 调用点
  - **完全没有监控日志**

- **SourceLog 表** (`backend/app/models/models.py:299-329`):
  - 已有 Lens 级别的日志记录
  - `extra_data` 字段（JSONB）可存储 token 统计
  - 当前只记录了 `duration_ms`

- **日志配置** (`backend/app/core/logging_config.py`):
  - 已配置 RotatingFileHandler
  - 格式：`%(asctime)s - %(name)s - %(levelname)s - %(message)s`
  - 需要增强支持结构化 JSON 日志

## 实现方案

### 1. 创建 LLM 监控装饰器/包装器

**文件**: `backend/app/core/llm_monitor.py`

功能：
- 包装 `AsyncOpenAI.chat.completions.create` 调用
- 自动记录：
  - 请求参数（model, messages, temperature 等）
  - 响应数据（content, finish_reason）
  - Token 使用量（prompt_tokens, completion_tokens, total_tokens）
  - 耗时（毫秒）
  - 成本估算（基于 token 价格表）
  - 上下文信息（lens_key, source_id）
- 输出结构化 JSON 日志

### 2. 增强日志配置

**文件**: `backend/app/core/logging_config.py`

改动：
- 添加专门的 `llm_monitor` logger
- 配置 JSON formatter（使用 `python-json-logger`）
- 独立的日志文件：`logs/llm_calls.jsonl`（每行一个 JSON）

### 3. 集成到现有服务

**文件**: `backend/app/services/runner_service.py`

改动：
- 在 `run_lens` 方法中使用监控包装器
- 将 token 统计添加到 `Artifact.usage` 字段
- 更新 SourceLog 的 `extra_data` 包含完整 token 信息

**文件**: `backend/app/services/generator_service.py`

改动：
- 在 `_call_llm` 方法中添加监控

### 4. 数据结构设计

#### 细粒度日志（每次 API 调用）
```json
{
  "timestamp": "2025-02-14T10:30:45.123Z",
  "level": "INFO",
  "logger": "llm_monitor",
  "event": "llm_api_call",
  "context": {
    "lens_key": "default_summary",
    "source_id": "uuid",
    "service": "RunnerService"
  },
  "request": {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": null,
    "messages_count": 2,
    "system_prompt_length": 150,
    "user_prompt_length": 2500,
    "has_images": true,
    "image_count": 3
  },
  "response": {
    "content_length": 1200,
    "finish_reason": "stop"
  },
  "usage": {
    "prompt_tokens": 3500,
    "completion_tokens": 800,
    "total_tokens": 4300
  },
  "timing": {
    "duration_ms": 2340,
    "start_time": "2025-02-14T10:30:42.783Z",
    "end_time": "2025-02-14T10:30:45.123Z"
  },
  "cost": {
    "prompt_cost_usd": 0.035,
    "completion_cost_usd": 0.024,
    "total_cost_usd": 0.059
  }
}
```

#### 粗粒度日志（Lens 级别汇总）
在现有 SourceLog 基础上增强 `extra_data`：
```json
{
  "total_api_calls": 3,
  "total_tokens": 12500,
  "prompt_tokens": 9000,
  "completion_tokens": 3500,
  "total_cost_usd": 0.175,
  "avg_duration_ms": 2100,
  "models_used": ["gpt-4", "gpt-4-vision"]
}
```

## 实现步骤

### Step 1: 创建监控核心模块
- 创建 `backend/app/core/llm_monitor.py`
- 实现 `LLMCallMonitor` 类
- 实现 `track_llm_call` 装饰器/上下文管理器

### Step 2: 增强日志配置
- 修改 `backend/app/core/logging_config.py`
- 添加 JSON formatter
- 配置独立的 `llm_calls.jsonl` 文件

### Step 3: 集成到 RunnerService
- 修改 `run_lens` 方法包装 API 调用
- 收集 token 统计并更新 Artifact
- 更新 SourceLog 的 extra_data

### Step 4: 集成到 GeneratorService
- 修改 `_call_llm` 方法添加监控

### Step 5: 添加成本计算配置
- 在 `backend/app/core/config.py` 添加 token 价格配置
- 支持不同模型的价格表

## 依赖
- `python-json-logger`: 用于 JSON 格式日志输出
- OpenAI SDK 已返回 `usage` 信息，无需额外依赖

## 优势
1. **零侵入**：通过装饰器/包装器实现，不改变业务逻辑
2. **双粒度**：同时支持细粒度和粗粒度监控
3. **结构化**：JSON 格式方便后续分析（可用 jq, grep, ELK 等工具）
4. **可扩展**：易于添加新的监控指标（如错误率、重试次数等）
5. **成本透明**：实时计算每次调用的成本

## 后续扩展（可选）
- 添加 Prometheus metrics 导出
- 集成到 Grafana 可视化
- 异常检测（token 使用异常、耗时过长等）
- 按用户/Source 维度的成本统计 API
