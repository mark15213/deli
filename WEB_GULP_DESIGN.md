# Web Gulp 模式交互设计

## 一、现状分析

### 当前实现（`/gulp` 页面）

**布局结构：**
```
┌─────────────────────────────────────┐
│ Top Bar: [Back] 🥤 Gulping (1/30)  │
├─────────────────────────────────────┤
│                                     │
│         Vertical Snap Scroll        │
│         (一次显示一张卡片)            │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  GulpCard                     │  │
│  │  - Type badge + Source        │  │
│  │  - Content (Note/Quiz/Flash)  │  │
│  │  - Tags                       │  │
│  │  - [Clip] [Got it] 按钮       │  │
│  └───────────────────────────────┘  │
│                                     │
│  [Progress dots on right side]      │
└─────────────────────────────────────┘
```

**交互方式：**
- 滚轮/触摸板滑动切换卡片（snap scroll）
- 点击 "Clip" 书签卡片
- 点击 "Got it" 标记已学（调用 `submitReview(cardId, 3)`）
- Quiz 卡片可以点选选项，显示答案
- Flashcard 可以点击翻转

**问题：**
1. 交互单一 — 只有书签和"Got it"，没有提问、深入、跳过等丰富交互
2. 没有推荐模式切换 — 用户无法选择"复习"还是"探索"
3. Quiz 交互不完整 — 选择答案后没有反馈，直接显示答案
4. 没有键盘快捷键 — 无法用键盘快速操作

---

## 二、设计目标

基于 VISION.md 的设计，Web 端 Gulp 模式要实现：

1. **丰富的交互动作** — 提问、深入、跳过、举报
2. **推荐模式切换** — 复习/探索/混合/深入
3. **更好的答题体验** — 即时反馈、正确率追踪
4. **键盘快捷键** — 提升效率
5. **主动提问对话** — 核心新功能

---

## 三、新版 Gulp 页面设计

### 3.1 整体布局

```
┌──────────────────────────────────────────────────────────┐
│ Top Bar                                                  │
│ [Back] [复习][探索][混合][深入] 🥤 Gulping (1/30)        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│                  Vertical Snap Scroll                    │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Enhanced GulpCard                                 │  │
│  │                                                    │  │
│  │  [Type Badge]              [Source + External ↗]  │  │
│  │                                                    │  │
│  │  ┌──────────────────────────────────────────────┐ │  │
│  │  │                                              │ │  │
│  │  │         Card Content Area                    │ │  │
│  │  │  (Note / Quiz / Flashcard / Reading Note)    │ │  │
│  │  │                                              │ │  │
│  │  └──────────────────────────────────────────────┘ │  │
│  │                                                    │  │
│  │  [#tag1 #tag2 #tag3]                              │  │
│  │                                                    │  │
│  │  ┌──────────────────────────────────────────────┐ │  │
│  │  │ Action Bar (4 buttons)                       │ │  │
│  │  │ [💬 Ask] [🔖 Clip] [⬇️ Deep] [⏭ Skip]        │ │  │
│  │  └──────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  [Progress dots]                                         │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ Ask Dialog (半屏 Sheet，从底部弹出)                       │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Context Preview                                    │  │
│  │ 📄 Current Card: "Attention is All You Need"      │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Conversation                                       │  │
│  │ User: What is multi-head attention?                │  │
│  │ AI: Multi-head attention allows...                 │  │
│  │ User: How does it differ from single-head?        │  │
│  │ AI: The key difference is...                       │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  [Input: Type your question...] [Send] [Save as Card]   │
└──────────────────────────────────────────────────────────┘
```

### 3.2 顶部模式切换器

```tsx
<div className="flex items-center gap-2">
  <button
    className={mode === 'review' ? 'active' : ''}
    onClick={() => setMode('review')}
  >
    🔄 复习
  </button>
  <button
    className={mode === 'explore' ? 'active' : ''}
    onClick={() => setMode('explore')}
  >
    🔍 探索
  </button>
  <button
    className={mode === 'mixed' ? 'active' : ''}
    onClick={() => setMode('mixed')}
  >
    ⚖️ 混合
  </button>
  <button
    className={mode === 'deep_dive' ? 'active' : ''}
    onClick={() => setMode('deep_dive')}
  >
    🎯 深入
  </button>
</div>
```

**交互逻辑：**
- 点击切换模式 → 重新加载信息流（`fetchFeed(mode)`）
- 模式保存到 localStorage，下次打开记住
- 深入模式需要先选择一个 source（点击卡片的 source 标题进入）

### 3.3 增强的 GulpCard

#### 3.3.1 Action Bar（4 个按钮）

```tsx
<div className="action-bar">
  {/* 1. Ask - 主动提问 */}
  <button onClick={handleAsk}>
    <MessageCircle className="h-4 w-4" />
    Ask
  </button>

  {/* 2. Clip - 书签（已有） */}
  <button onClick={handleClip}>
    {isBookmarked ? <BookmarkCheck /> : <Bookmark />}
    {isBookmarked ? 'Clipped' : 'Clip'}
  </button>

  {/* 3. Deep Dive - 深入该 source */}
  <button onClick={handleDeepDive}>
    <ArrowDown className="h-4 w-4" />
    Deep
  </button>

  {/* 4. Skip - 跳过 */}
  <button onClick={handleSkip}>
    <SkipForward className="h-4 w-4" />
    Skip
  </button>
</div>
```

**按钮说明：**

| 按钮 | 功能 | API 调用 | 效果 |
|------|------|---------|------|
| Ask | 打开提问对话框 | 无（打开 Dialog） | 弹出半屏对话面板 |
| Clip | 书签/取消书签 | `POST/DELETE /bookmarks/{cardId}` | 图标变色，乐观更新 |
| Deep | 深入该 source | 切换到深入模式 | 信息流切换为该 source 的所有卡片 |
| Skip | 跳过该卡片 | `POST /study/gulp/{cardId}/engage` | 滚动到下一张，记录 skip 事件 |

#### 3.3.2 Quiz 卡片增强

**当前问题：**
- 选择答案后直接显示正确答案，没有"提交"按钮
- 没有正确/错误的视觉反馈

**改进方案：**

```tsx
// Quiz 交互流程
1. 用户点选选项 → 选项高亮，底部出现 "Check Answer" 按钮
2. 点击 "Check Answer" → 显示正确/错误反馈
   - 正确：绿色背景，✓ 图标，"Correct!" 提示
   - 错误：红色背景，✗ 图标，显示正确答案
3. 显示 Explanation（如果有）
4. 底部按钮变为 "Continue" → 点击滚动到下一张卡片
```

**代码结构：**

```tsx
const [selectedOption, setSelectedOption] = useState<number | null>(null)
const [isChecked, setIsChecked] = useState(false)
const [isCorrect, setIsCorrect] = useState(false)

const handleCheck = () => {
  const correct = options[selectedOption] === card.answer
  setIsCorrect(correct)
  setIsChecked(true)

  // 记录答题结果
  trackEngagement(card.id, 'answer', { is_correct: correct })
}

const handleContinue = () => {
  // 滚动到下一张
  scrollToNext()
}
```

#### 3.3.3 Reading Note 卡片增强

**当前问题：**
- Reading Note 内容可能很长，需要滚动
- 没有"系列"的概念（batch 信息没有充分利用）

**改进方案：**

```tsx
// Reading Note 顶部显示系列进度
{card.batch_index != null && card.batch_total != null && (
  <div className="batch-progress">
    <div className="progress-bar">
      <div
        className="progress-fill"
        style={{ width: `${((card.batch_index + 1) / card.batch_total) * 100}%` }}
      />
    </div>
    <span className="text-xs">
      Part {card.batch_index + 1} of {card.batch_total}
    </span>
  </div>
)}
```

### 3.4 Ask Dialog（提问对话框）

**触发方式：**
- 点击 "Ask" 按钮
- 键盘快捷键：`A` 键

**布局：**

```tsx
<Dialog open={askDialogOpen} onOpenChange={setAskDialogOpen}>
  <DialogContent className="max-w-3xl h-[70vh] flex flex-col">
    {/* Header */}
    <DialogHeader>
      <DialogTitle>Ask about this card</DialogTitle>
      <DialogDescription>
        Ask questions about "{card.question.slice(0, 50)}..."
      </DialogDescription>
    </DialogHeader>

    {/* Context Preview (可折叠) */}
    <Collapsible>
      <CollapsibleTrigger>
        📄 Context: {card.source_title}
      </CollapsibleTrigger>
      <CollapsibleContent>
        <div className="text-sm text-muted-foreground">
          {card.question}
          {card.answer && <p>{card.answer.slice(0, 200)}...</p>}
        </div>
      </CollapsibleContent>
    </Collapsible>

    {/* Conversation Area (scrollable) */}
    <ScrollArea className="flex-1 pr-4">
      {messages.map((msg, i) => (
        <div key={i} className={msg.role === 'user' ? 'user-message' : 'ai-message'}>
          <div className="avatar">{msg.role === 'user' ? '👤' : '🤖'}</div>
          <div className="content">
            <ReactMarkdown>{msg.content}</ReactMarkdown>
          </div>
          {msg.role === 'assistant' && (
            <button onClick={() => handleSaveAsCard(i)}>
              💾 Save as Card
            </button>
          )}
        </div>
      ))}
      {isLoading && <Loader2 className="animate-spin" />}
    </ScrollArea>

    {/* Input Area */}
    <div className="flex gap-2">
      <Input
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Type your question..."
        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
      />
      <Button onClick={handleSend} disabled={!question.trim() || isLoading}>
        <Send className="h-4 w-4" />
      </Button>
    </div>
  </DialogContent>
</Dialog>
```

**交互流程：**

```
1. 用户点击 "Ask" → 打开 Dialog
2. 输入问题 → 点击 Send 或按 Enter
3. 调用 API: POST /ask { card_id, question, conversation_id }
4. 显示 AI 回答（流式或一次性）
5. 用户可以继续追问（多轮对话）
6. 点击 "Save as Card" → 将 Q&A 保存为新卡片
7. 关闭 Dialog → 返回信息流
```

### 3.5 Deep Dive 模式

**触发方式：**
- 点击卡片的 Source 标题
- 点击 "Deep" 按钮

**效果：**
- 顶部模式切换器自动切换到"深入"模式
- 显示该 Source 的标题和摘要（如果有）
- 信息流只显示该 Source 的所有卡片（按 batch 排序）
- 顶部增加 "Exit Deep Dive" 按钮

**实现：**

```tsx
const handleDeepDive = (sourceMaterialId: string) => {
  setMode('deep_dive')
  setDeepDiveSourceId(sourceMaterialId)
  fetchFeed('deep_dive', sourceMaterialId)
}

const handleExitDeepDive = () => {
  setMode('mixed')
  setDeepDiveSourceId(null)
  fetchFeed('mixed')
}
```

**API 调用：**
```
GET /study/gulp?mode=deep_dive&source_material_id={id}
```

### 3.6 键盘快捷键

| 按键 | 功能 | 说明 |
|------|------|------|
| `↓` / `Space` | 下一张卡片 | 滚动到下一张 |
| `↑` | 上一张卡片 | 滚动到上一张 |
| `A` | Ask | 打开提问对话框 |
| `B` | Bookmark | 书签/取消书签 |
| `D` | Deep Dive | 深入该 source |
| `S` | Skip | 跳过该卡片 |
| `Enter` | 提交答案 | Quiz 卡片：提交选择的答案 |
| `1-4` | 选择选项 | Quiz 卡片：快速选择选项 A-D |
| `Esc` | 关闭对话框 | 关闭 Ask Dialog |

**实现：**

```tsx
useEffect(() => {
  const handleKeyDown = (e: KeyboardEvent) => {
    // 如果在输入框中，不触发快捷键
    if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
      return
    }

    switch (e.key.toLowerCase()) {
      case 'arrowdown':
      case ' ':
        e.preventDefault()
        scrollToNext()
        break
      case 'arrowup':
        e.preventDefault()
        scrollToPrev()
        break
      case 'a':
        setAskDialogOpen(true)
        break
      case 'b':
        handleBookmarkToggle()
        break
      case 'd':
        handleDeepDive(currentCard.source_material_id)
        break
      case 's':
        handleSkip()
        break
      // ... 其他快捷键
    }
  }

  window.addEventListener('keydown', handleKeyDown)
  return () => window.removeEventListener('keydown', handleKeyDown)
}, [currentCard])
```

---

## 四、API 变更

### 4.1 改造现有端点

```typescript
// GET /study/gulp
interface GulpFeedRequest {
  limit?: number          // 默认 30
  offset?: number         // 默认 0
  mode?: 'review' | 'explore' | 'mixed' | 'deep_dive'  // 新增
  source_material_id?: string  // 深入模式需要
}

interface GulpFeedResponse {
  cards: GulpCard[]
  total: number
  has_more: boolean
  mode: string           // 返回当前模式
  source_info?: {        // 深入模式时返回 source 信息
    id: string
    title: string
    summary?: string
  }
}
```

### 4.2 新增端点

```typescript
// POST /ask - 主动提问
interface AskRequest {
  card_id: string
  question: string
  conversation_id?: string  // 多轮对话
}

interface AskResponse {
  answer: string
  conversation_id: string
  suggested_card?: {        // 建议保存为卡片
    question: string
    answer: string
  }
}

// GET /ask/conversations - 对话历史
interface ConversationListResponse {
  conversations: Array<{
    id: string
    card_id: string
    title: string
    created_at: string
  }>
}

// GET /ask/conversations/{id} - 对话详情
interface ConversationDetailResponse {
  id: string
  card_id: string
  messages: Array<{
    role: 'user' | 'assistant'
    content: string
  }>
}

// POST /ask/conversations/{id}/save-card - 保存为卡片
interface SaveCardRequest {
  message_index: number  // 保存哪条 Q&A
}

// POST /study/gulp/{card_id}/engage - 行为追踪
interface EngageRequest {
  event_type: 'view' | 'answer' | 'skip' | 'bookmark' | 'ask' | 'deep_dive'
  duration_ms?: number
  is_correct?: boolean
  extra_data?: Record<string, any>
}

// PATCH /users/me/settings - 更新用户设置
interface UpdateSettingsRequest {
  gulp_mode?: 'review' | 'explore' | 'mixed' | 'deep_dive'
}
```

---

## 五、组件结构

```
web/src/app/gulp/
├── page.tsx                    # 主页面（改造）
└── components/
    ├── GulpCard.tsx            # 卡片组件（改造）
    ├── GulpModeSwitch.tsx      # 模式切换器（新增）
    ├── AskDialog.tsx           # 提问对话框（新增）
    ├── DeepDiveHeader.tsx      # 深入模式头部（新增）
    └── KeyboardShortcuts.tsx   # 快捷键提示（新增）

web/src/lib/api/
├── study.ts                    # 改造：增加 mode 参数
└── ask.ts                      # 新增：提问相关 API
```

---

## 六、实施步骤

### Phase 1：基础改造（1-2 天）

1. **改造 GulpCard 组件**
   - 增加 4 个 Action 按钮（Ask, Clip, Deep, Skip）
   - 改进 Quiz 交互（Check Answer → Continue）
   - 增加 Reading Note 系列进度条

2. **增加模式切换器**
   - 顶部增加 4 个模式按钮
   - 切换模式时重新加载信息流
   - 模式保存到 localStorage

3. **改造 API 调用**
   - `getGulpFeed` 增加 `mode` 参数
   - 后端 `/study/gulp` 支持 `mode` 参数（简化版：只是过滤逻辑）

### Phase 2：Ask 功能（2-3 天）

4. **创建 AskDialog 组件**
   - 半屏 Dialog 布局
   - 对话消息列表
   - 输入框 + 发送按钮

5. **实现 Ask API**
   - 后端 `POST /ask` 端点
   - LLM 调用 + 上下文构建
   - 对话历史存储

6. **集成到 GulpCard**
   - 点击 "Ask" 按钮打开 Dialog
   - 传递当前卡片上下文
   - "Save as Card" 功能

### Phase 3：Deep Dive + 快捷键（1 天）

7. **Deep Dive 模式**
   - 点击 Source 标题进入深入模式
   - 顶部显示 Source 信息
   - "Exit Deep Dive" 按钮

8. **键盘快捷键**
   - 实现快捷键监听
   - 快捷键提示组件（可选）

### Phase 4：行为追踪（1 天）

9. **行为追踪 API**
   - 后端 `POST /study/gulp/{card_id}/engage` 端点
   - 前端调用：skip, answer, ask 等事件

10. **数据分析准备**
    - 后端存储 engagement 数据
    - 为后续推荐算法优化做准备

---

## 七、设计细节

### 7.1 视觉设计

**配色方案：**
- Ask 按钮：蓝色（`text-blue-600`）
- Clip 按钮：琥珀色（`text-amber-600`）
- Deep 按钮：紫色（`text-purple-600`）
- Skip 按钮：灰色（`text-gray-600`）

**动画效果：**
- 按钮 hover：轻微放大（`scale-105`）
- 卡片切换：平滑滚动（`scroll-behavior: smooth`）
- Dialog 打开：从底部滑入（`slide-in-from-bottom`）
- 答题反馈：背景色渐变（`transition-colors duration-300`）

### 7.2 响应式设计

**桌面端（> 1024px）：**
- 卡片最大宽度：`max-w-3xl`
- Action Bar：4 个按钮横排
- Ask Dialog：宽度 `max-w-3xl`，高度 `70vh`

**平板端（768px - 1024px）：**
- 卡片最大宽度：`max-w-2xl`
- Action Bar：4 个按钮横排（稍小）
- Ask Dialog：宽度 `max-w-2xl`，高度 `60vh`

**移动端（< 768px）：**
- 卡片全宽
- Action Bar：2x2 网格布局
- Ask Dialog：全屏（`h-screen`）

### 7.3 性能优化

**虚拟滚动：**
- 当前实现已经是 snap scroll，性能较好
- 如果卡片数量 > 100，考虑虚拟滚动（react-window）

**图片懒加载：**
- 使用 `loading="lazy"` 属性
- 只加载当前可见卡片的图片

**API 缓存：**
- 使用 SWR 或 React Query 缓存 API 响应
- 模式切换时优先使用缓存

---

## 八、用户体验优化

### 8.1 空状态

**无卡片时：**
```tsx
<div className="empty-state">
  <Coffee className="h-16 w-16" />
  <h2>Nothing to gulp yet</h2>
  <p>Subscribe to some decks to get started</p>
  <Button onClick={() => router.push('/decks')}>
    Browse Decks
  </Button>
</div>
```

**深入模式无卡片时：**
```tsx
<div className="empty-state">
  <FileQuestion className="h-16 w-16" />
  <h2>No cards from this source</h2>
  <Button onClick={handleExitDeepDive}>
    Back to Feed
  </Button>
</div>
```

### 8.2 加载状态

**初始加载：**
- 显示骨架屏（3 张卡片的轮廓）

**分页加载：**
- 底部显示 Spinner
- 提前 5 张卡片时触发加载

**Ask 对话加载：**
- 输入框禁用
- 显示"AI is thinking..."动画

### 8.3 错误处理

**API 错误：**
- Toast 提示错误信息
- 提供 "Retry" 按钮

**网络断开：**
- 显示离线提示
- 缓存已加载的卡片，允许继续浏览

---

## 九、总结

这个设计将 Web Gulp 模式从一个简单的卡片浏览器，升级为一个功能丰富的沉浸式学习工具：

**核心改进：**
1. ✅ 4 种推荐模式（复习/探索/混合/深入）
2. ✅ 主动提问对话（Ask）
3. ✅ 深入某个 source（Deep Dive）
4. ✅ 丰富的交互动作（Ask/Clip/Deep/Skip）
5. ✅ 键盘快捷键支持
6. ✅ 改进的 Quiz 交互体验

**技术栈：**
- React + TypeScript
- Tailwind CSS + Radix UI
- React Markdown（对话渲染）
- SWR / React Query（API 缓存）

**开发时间估算：**
- Phase 1（基础改造）：1-2 天
- Phase 2（Ask 功能）：2-3 天
- Phase 3（Deep Dive + 快捷键）：1 天
- Phase 4（行为追踪）：1 天
- **总计：5-7 天**

要开始实现吗？我建议先从 Phase 1 开始，快速验证交互逻辑。
