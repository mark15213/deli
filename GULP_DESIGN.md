# Gulp - 软件平台架构与设计文档

## 1. 核心产品概念
Gulp 是一个集信息流订阅、知识生成、以及知识卡片消费于一体的软件平台。
- **Feed (信息流)**: 订阅的原始信息或经过初步筛选的内容流。
- **Knowledge (知识)**: 从信息流中提炼、生成的结构化知识库。
- **Gulp (消费)**: 类似 Duolingo 交互 + 抖音上下滑动体验的知识卡片消费模块。

---

## 2. 技术栈选择建议

考虑到需要覆盖 Web 端和 iOS 端，并且包含复杂的交互（抖音式滑动、Duolingo式问答）以及 AI 相关的知识生成，推荐以下技术栈组合：

### 方案 A：大前端跨平台 + AI 后端（推荐，开发效率最高）
*适合全栈独立开发者或小团队快速迭代*

- **前端 (Web & iOS): React Native + Expo**
  - **原因**: 能够一套代码同时编译到 iOS 和 Web（Expo Web）。结合 `react-native-reanimated` 可以完美实现类似抖音的丝滑上下滑动效果以及卡片翻转等复杂动画。
  - **UI 框架**: Tamagui (支持 RN 和 Web 的高性能样式库) 或 NativeWind (Tailwind 的 RN 版)。
  - **状态管理**: Zustand 或 Jotai。

### 方案 B：双前端原生体验 + AI 后端（推荐，性能和 SEO 最佳）
*适合对 Web 端 SEO 有要求，且对 iOS 体验要求极高的场景*

- **Web 端: Next.js (React)**
  - 利用 App Router, TailwindCSS, Framer Motion 实现丝滑的网页端交互。支持良好的 SEO，方便信息的公开分享。
- **iOS 端: Swift (SwiftUI) 或 React Native**
  - 如果追求极致原生体验和最佳的滑动性能，原生 SwiftUI 在实现信息流和卡片堆叠上非常高效。
- **后端 (API & AI): Python (FastAPI)**
  - **原因**: 平台涉及“知识生成”，大概率需要接入 LLM (大语言模型)、RAG (检索增强生成)、LangChain / LlamaIndex 等，Python 是 AI 领域的绝对主力。FastAPI 性能极高，且原生支持异步，非常适合 IO 密集型和 AI 调用。
- **数据库**:
  - **关系型数据库**: PostgreSQL (存储用户、订阅关系、卡片状态、知识图谱基础数据)。
  - **缓存/消息队列**: Redis (用于 Feed 流的分发、缓存用户的学习进度和卡片复习算法)。

---

## 3. 代码目录结构设计 (推荐 Monorepo 结构)

采用 Turborepo + pnpm workspace 的 Monorepo 结构，方便共享 API 类型定义和公共逻辑。

```text
gulp-workspace/
├── apps/
│   ├── web/                 # Next.js Web 端应用
│   │   ├── src/
│   │   │   ├── app/         # 页面路由
│   │   │   │   ├── feed/    # 信息流页面
│   │   │   │   ├── knowledge/ # 知识库管理页面
│   │   │   │   └── gulp/    # 知识卡片消费页面
│   │   │   ├── components/  # 组件库 (抖音滑动组件、Duolingo问答组件)
│   │   │   └── lib/         # 工具函数、状态管理
│   │   └── package.json
│   │
│   ├── ios/                 # React Native / Expo iOS 端应用
│   │   ├── src/
│   │   │   ├── app/         # Expo Router 路由 (Tabs)
│   │   │   ├── components/  # 移动端原生优化组件
│   │   │   └── hooks/       # 动画 Hooks, 交互 Hooks
│   │   └── package.json
│   │
│   └── api/                 # FastAPI Python 后端 (可以通过 submodule 管理或放同级)
│       ├── app/
│       │   ├── api/         # 路由层 (Controllers)
│       │   │   ├── v1/
│       │   │   │   ├── feed.py      # 订阅与推流接口
│       │   │   │   ├── knowledge.py # 知识图谱、节点接口
│       │   │   │   └── gulp.py      # 卡片分发、学习进度(Spaced Repetition)接口
│       │   ├── core/        # 配置、权限、安全
│       │   ├── models/      # ORM 模型 (SQLAlchemy)
│       │   ├── schemas/     # Pydantic 验证模型 (Input/Output)
│       │   └── services/    # 核心业务逻辑
│       │       ├── llm.py           # 大模型调用封装，负责"知识生成"
│       │       ├── srs.py           # 间隔重复算法(类似Anki/Duolingo) 
│       │       └── feed_engine.py   # 信息流推荐与聚合逻辑
│       ├── requirements.txt
│       └── main.py
│
├── packages/                # 共享包 (如果 Web 和 iOS 都用 React 生态)
│   ├── shared-types/        # TypeScript 接口定义 (与后端 Pydantic 同步)
│   ├── ui/                  # 跨平台共享 UI 组件
│   └── tsconfig/            # 共享的 TypeScript 配置
│
└── package.json             # 根工作区配置
```

## 4. 关键技术难点与建议
1. **类似抖音的 Feed 消费体验**: 核心在于**虚拟列表 (Virtualized List)** 和 **预加载 (Pre-fetching)**。在 RN 中使用 `@shopify/flash-list`，在 Web 中使用 `react-virtualized`，结合数据的分页预获取。
2. **Duolingo 式的知识问答**: 需要设计一套**卡片状态机**和**间隔重复算法 (Spaced Repetition System, SRS)**。后端依据用户的回答正误（Gulp 消费反馈）计算下一次卡片出现的权重。
3. **知识生成 (AI Pipeline)**: 订阅的信息源（如 RSS、网页、推文）抓取后，需要一个异步任务队列（如 Celery + RabbitMQ/Redis）让 LLM 后台处理，将无结构的文章提炼成结构化的 QA 卡片（Gulp）存入数据库。
