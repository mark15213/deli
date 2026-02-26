# Deli 愿景设计：高质量信息流 + 双向互动

## 一、核心问题

当前 Gulp 模式是一个简单的卡片浏览器：取 300 张最新卡片 → 书签优先 → 按 source 轮询 → 分页返回。用户只能"揭示答案"和"书签"，没有质量反馈、没有兴趣建模、没有主动提问能力。

要实现"移动端像刷短视频一样学习"的愿景，需要解决三个问题：

1. **内容从哪来，怎么保证质量？**
2. **信息流怎么排序，怎么个性化？**
3. **用户怎么互动，不只是被动消费？**

---

## 二、信息源与内容质量

### 2.1 内容来源体系

```
┌─────────────────────────────────────────────────────┐
│                    内容来源                           │
├──────────────┬──────────────┬───────────────────────┤
│  用户主动添加  │  订阅自动同步  │  社区/公共内容（后续）  │
├──────────────┼──────────────┼───────────────────────┤
│ arXiv 论文    │ RSS Feed     │ 公开 Deck 订阅         │
│ Web 文章      │ HF Daily     │ 精选内容推荐           │
│ PDF 上传      │ Author Blog  │ 用户分享的高质量卡片    │
│ 手动笔记      │ GitHub Repo  │                       │
│ Tweet Thread  │              │                       │
└──────────────┴──────────────┴───────────────────────┘
```

现有来源已经很丰富。第一版不需要新增来源类型，重点是**提升已有内容的质量**。

### 2.2 内容质量保障：三层过滤

```
Source → Pipeline 生成卡片 → [质量评分] → [用户审核] → 信息流
                               ↑              ↑
                          自动过滤低质量     Inbox 审批
```

**第一层：Pipeline 生成质量提升**

在现有 Pipeline 中增加一个 `card_quality_scorer` 算子（LLM），对生成的每张卡片打分：

```yaml
# 评分维度（1-5 分）
clarity: 问题表述是否清晰
relevance: 是否抓住了源材料的关键点
difficulty: 难度是否适中（不太简单也不太难）
standalone: 脱离原文是否能独立理解
```

- 综合分 < 3 的卡片自动标记为 REJECTED
- 综合分 3-4 的卡片进入 PENDING（需用户审核）
- 综合分 > 4 的卡片直接 ACTIVE

存储：`Card.content.quality_score: float` + `Card.content.quality_details: dict`

**第二层：用户隐式反馈**

追踪用户在信息流中的行为信号，反向调整内容质量权重：

| 信号 | 含义 | 权重影响 |
|------|------|---------|
| 停留时间 > 5s | 认真阅读 | +quality |
| 书签 | 高价值 | +quality |
| 回答正确 | 难度合适 | +quality |
| 快速滑过 (< 1s) | 不感兴趣/低质量 | -quality |
| 回答错误 | 可能太难或表述不清 | 中性（需更多信号） |
| 主动提问 | 深度参与 | +quality |
| 长按/举报 | 有问题 | -quality |

新增 `CardEngagement` 表记录这些信号（见第四节数据模型）。

**第三层：Source 级质量追踪**

聚合某个 Source 下所有卡片的用户反馈，计算 Source 质量分：

```python
source_quality = avg(card_quality_scores) * 0.4 + avg(engagement_scores) * 0.6
```

低质量 Source 的卡片在信息流中降权。用户可以在设置中看到每个 Source 的质量评分，决定是否继续订阅。

---

## 三、信息流推荐算法

### 3.1 整体架构

```
用户打开 Gulp → 请求信息流
                    ↓
            ┌───────────────┐
            │  候选池生成     │  从订阅 Deck 中取 ACTIVE 卡片
            │  (300 张)      │  + FSRS 到期过滤
            └───────┬───────┘
                    ↓
            ┌───────────────┐
            │  多路召回       │  按不同策略各取一批
            │               │  ① 巩固：FSRS 到期卡片
            │               │  ② 探索：新内容/新 topic
            │               │  ③ 书签：用户标记的重点
            │               │  ④ 热门：高 engagement 卡片
            └───────┬───────┘
                    ↓
            ┌───────────────┐
            │  排序 & 混合    │  用户配置的比例混合
            │               │  + 多样性保障（source 去重）
            │               │  + 质量加权
            └───────┬───────┘
                    ↓
            ┌───────────────┐
            │  分页返回       │  30 张/页，无限滚动
            └───────────────┘
```

### 3.2 用户可配置的推荐模式

存储在 `User.settings.gulp_mode`：

```python
class GulpMode(str, Enum):
    REINFORCE = "reinforce"   # 巩固为主：80% 到期复习 + 20% 新内容
    BALANCED = "balanced"     # 均衡：50% 复习 + 50% 新内容
    EXPLORE = "explore"       # 探索为主：20% 复习 + 80% 新内容
    DEEP_DIVE = "deep_dive"   # 深入模式：聚焦某个 source/topic 的所有卡片
```

### 3.3 排序公式

每张卡片的最终得分：

```python
score = (
    quality_weight * quality_score          # 内容质量（0-1）
    + freshness_weight * freshness_score    # 新鲜度（越新越高）
    + relevance_weight * relevance_score    # 与用户兴趣的相关度
    + urgency_weight * urgency_score        # FSRS 紧迫度（越过期越高）
    + bookmark_bonus                        # 书签加分
    + diversity_penalty                     # 同 source 连续出现的惩罚
)
```

权重根据用户选择的 GulpMode 动态调整。

### 3.4 Topic 自动分类（AI 驱动）

在 Pipeline 中增加 `topic_extractor` 算子，对每个 SourceMaterial 提取 topics：

```python
# SourceMaterial.rich_data.topics
{
    "topics": [
        {"name": "Transformer Architecture", "confidence": 0.95},
        {"name": "Attention Mechanism", "confidence": 0.88},
        {"name": "Natural Language Processing", "confidence": 0.82}
    ],
    "domain": "Machine Learning"  # 顶级领域
}
```

Topics 用于：
- 信息流中的多样性保障（避免连续推同一 topic）
- 用户兴趣建模（基于 engagement 数据推断兴趣 topic）
- 后续技能量化的基础

---

## 四、双向互动设计

### 4.1 信息流中的交互动作

当前 Gulp 只有 2 个动作（揭示 + 书签）。新设计扩展为丰富的交互：

```
┌─────────────────────────────────────────┐
│              Gulp 卡片                   │
│                                         │
│  [问题内容]                              │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │  MCQ: 点选选项                    │    │
│  │  Cloze: 输入答案                  │    │
│  │  Flashcard: 点击翻转              │    │
│  │  Reading Note: 滑动阅读           │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ─────────── 操作栏 ───────────         │
│  [💬 提问]  [🔖 书签]  [⬇️ 深入]  [⏭ 跳过] │
│                                         │
└─────────────────────────────────────────┘
```

**新增交互：**

| 动作 | 触发方式 | 效果 |
|------|---------|------|
| 回答问题 | 点选/输入 | 记录正确率，影响 FSRS + 推荐 |
| 提问 | 点击💬按钮 | 打开对话面板，基于当前卡片上下文提问 |
| 深入 | 点击⬇️按钮 | 展开该 source 的更多卡片（reading notes 系列） |
| 跳过 | 快速上滑 / 点击⏭ | 记录为"不感兴趣"，降低同类内容权重 |
| 长按 | 长按卡片 | 弹出菜单：举报质量问题 / 查看原文 / 分享 |

### 4.2 主动提问（Ask）

这是最关键的新功能。用户在信息流中看到一张卡片后，可以基于卡片内容提问。

**交互流程：**

```
用户看到一张关于 "Attention is All You Need" 的 reading note
    ↓
点击 💬 提问按钮
    ↓
底部弹出对话面板（半屏，类似 iOS Sheet）
    ↓
预填上下文：当前卡片内容 + 原文摘要
    ↓
用户输入："Multi-head attention 和 single-head 相比有什么优势？"
    ↓
LLM 基于原文上下文回答
    ↓
用户可以继续追问（多轮对话）
    ↓
对话结束后，系统可以：
  - 将 Q&A 保存为新卡片（用户确认）
  - 记录为高参与度信号
  - 更新用户兴趣模型
```

**后端实现：**

```
POST /api/v1/ask
{
    "card_id": "uuid",                    // 当前卡片
    "question": "用户的问题",
    "conversation_id": "uuid" | null      // 多轮对话 ID
}

Response:
{
    "answer": "LLM 的回答",
    "conversation_id": "uuid",
    "suggested_card": { ... } | null      // 建议保存为卡片
}
```

**上下文构建策略：**

```python
context = {
    "card_content": card.content,                    # 当前卡片
    "source_summary": source_material.rich_data.summary,  # 原文摘要
    "related_cards": get_related_cards(card, limit=3),     # 同 batch 的其他卡片
    "conversation_history": get_conversation(conv_id),      # 之前的对话
}
```

### 4.3 深入模式（Deep Dive）

用户点击"深入"后，信息流临时切换为该 Source 的所有卡片：

```
正常信息流: [Card A - Paper1] [Card B - Paper2] [Card C - Paper3] ...
                                    ↓ 用户点击"深入" Card B
深入模式:   [Paper2 Summary] [Reading Note 1/9] [Note 2/9] ... [Quiz 1] [Quiz 2]
                                    ↓ 用户上滑退出
回到正常信息流: [Card C - Paper3] [Card D - Paper1] ...
```

这复用了现有的 batch 机制，只需要一个新的 API 参数：

```
GET /study/gulp?source_material_id={id}  → 返回该 source 的所有卡片（按 batch 排序）
```

---

## 五、数据模型变更

### 5.1 新增表：CardEngagement（用户行为追踪）

```python
class CardEngagement(Base):
    """用户与卡片的交互行为记录"""
    __tablename__ = "card_engagements"

    id: UUID
    user_id: UUID          # FK → users
    card_id: UUID          # FK → cards

    # 行为类型
    event_type: str        # "view", "answer", "skip", "bookmark", "ask", "deep_dive", "report"

    # 行为数据
    duration_ms: int | None       # 停留时间
    is_correct: bool | None       # 回答是否正确（仅 answer 类型）
    extra_data: dict              # 其他数据（如用户选择的选项、提问内容等）

    created_at: datetime
```

### 5.2 新增表：Conversation（提问对话）

```python
class Conversation(Base):
    """用户提问的对话记录"""
    __tablename__ = "conversations"

    id: UUID
    user_id: UUID          # FK → users
    card_id: UUID          # FK → cards（触发对话的卡片）
    source_material_id: UUID | None  # FK → source_materials

    title: str | None      # 对话标题（自动生成）
    messages: list[dict]   # [{role: "user"/"assistant", content: "..."}]

    created_at: datetime
    updated_at: datetime
```

### 5.3 扩展现有模型

```python
# Card.content 新增字段
{
    "quality_score": 4.2,           # Pipeline 自动评分
    "quality_details": {            # 评分细节
        "clarity": 4, "relevance": 5,
        "difficulty": 4, "standalone": 4
    }
}

# SourceMaterial.rich_data 新增字段
{
    "topics": [...],                # AI 提取的主题
    "domain": "Machine Learning",   # 顶级领域
    "source_quality": 0.85          # 聚合质量分
}

# User.settings 新增字段
{
    "gulp_mode": "balanced",        # 推荐模式
    "daily_goal": 20,               # 每日目标卡片数
    "topics_of_interest": [...]     # 用户手动标记的兴趣（可选）
}
```

---

## 六、API 变更

### 6.1 改造现有端点

```
GET /study/gulp
  新增参数:
    - mode: GulpMode = "balanced"           # 推荐模式
    - source_material_id: UUID | None       # 深入模式：只看某个 source
    - topic: str | None                     # 按 topic 过滤（后续）

  响应新增字段:
    GulpCard:
      + quality_score: float | None
      + topics: list[str]
```

### 6.2 新增端点

```
# 行为追踪
POST /study/gulp/{card_id}/engage
  Body: { event_type, duration_ms?, is_correct?, extra_data? }

# 主动提问
POST /ask
  Body: { card_id, question, conversation_id? }
  Response: { answer, conversation_id, suggested_card? }

# 对话历史
GET /ask/conversations
GET /ask/conversations/{id}

# 将对话 Q&A 保存为卡片
POST /ask/conversations/{id}/save-card
  Body: { message_index }  # 保存哪条 Q&A

# 推荐模式设置
PATCH /users/me/settings
  Body: { gulp_mode: "balanced" }
```

---

## 七、iOS 端变更

### 7.1 GulpCardView 改造

```
当前:  [揭示答案]  [书签]
改为:  [💬 提问]  [🔖 书签]  [⬇️ 深入]

+ 卡片内嵌交互（MCQ 点选、Cloze 输入）
+ 快速上滑 = 跳过（记录 skip 事件）
+ 停留时间自动追踪
+ 长按弹出菜单
```

### 7.2 新增 AskSheet

```
半屏 Sheet，包含：
- 上下文预览（当前卡片摘要）
- 消息列表（对话历史）
- 输入框 + 发送按钮
- "保存为卡片" 按钮（在 AI 回答旁边）
```

### 7.3 新增 DeepDiveView

```
全屏视图，展示某个 Source 的所有卡片：
- 顶部：Source 标题 + 摘要
- 卡片列表：按 batch 排序（Reading Notes → Flashcards → Quiz）
- 底部：返回信息流按钮
```

### 7.4 推荐模式切换

```
Gulp 页面顶部增加模式选择器：
[巩固] [均衡] [探索] [深入]
点击切换，重新加载信息流
```

---

## 八、实施路径

### Phase 1：行为追踪 + 信息流改造（MVP）

**后端：**
1. 新增 `card_engagements` 表 + Alembic migration
2. 新增 `POST /study/gulp/{card_id}/engage` 端点
3. 改造 `GET /study/gulp`：
   - 支持 `mode` 参数（四种模式）
   - 支持 `source_material_id` 参数（深入模式）
   - 加入质量加权排序
4. 新增 `PATCH /users/me/settings` 端点

**iOS：**
5. GulpCardView 增加交互动作（提问按钮、深入按钮、跳过手势）
6. 卡片内嵌答题交互（MCQ 点选、Cloze 输入）
7. 停留时间追踪 + engage API 调用
8. 顶部模式选择器
9. DeepDiveView（深入某个 source）

### Phase 2：主动提问（Ask）

**后端：**
1. 新增 `conversations` 表 + migration
2. 实现 `POST /ask` 端点（LLM 调用 + 上下文构建）
3. 实现对话历史 API
4. 实现 "保存为卡片" API

**iOS：**
5. AskSheet 组件（半屏对话面板）
6. 对话历史页面
7. "保存为卡片" 交互

### Phase 3：内容质量 + Topic 分类

**后端：**
1. Pipeline 新增 `card_quality_scorer` 算子
2. Pipeline 新增 `topic_extractor` 算子
3. 信息流排序加入 quality_score 和 topic 多样性
4. Source 级质量聚合

### Phase 4：技能量化（规划，不急实现）

- 基于 topic + FSRS 数据计算领域掌握度
- 技能树可视化
- 学习路径推荐

---

## 九、关键设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 推荐算法 | 规则 + 权重，非 ML | 数据量小，规则可解释，迭代快 |
| Topic 分类 | LLM 提取，非预定义分类 | 灵活，不需要维护分类体系 |
| 质量评分 | LLM 打分 + 用户反馈 | 双重保障，LLM 做初筛，用户做终审 |
| 提问上下文 | 卡片 + 摘要 + 同 batch 卡片 | 平衡上下文丰富度和 token 成本 |
| 行为追踪 | 异步写入，不阻塞 UI | 不影响滑动体验 |
| 推荐模式 | 用户手动切换 | 给用户控制权，避免算法黑箱 |
