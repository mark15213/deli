# Gulp

AI 驱动的知识学习平台 —— 将论文、文章、笔记等多种来源的内容，通过 AI 自动提炼为闪卡、阅读笔记和测验题，结合 FSRS 间隔重复算法进行高效学习。

## 核心流程

```
内容摄入 → AI Lens 处理 → 卡片生成 → 间隔重复学习
```

**支持的内容来源：** arXiv 论文、网页文章、PDF 文档、RSS 订阅、Notion 知识库、HuggingFace 每日论文、手动笔记等

**AI Lens 系统：** 可配置的 AI 处理管线，基于 YAML 定义 prompt 模板，支持：
- 内容摘要（TL;DR）
- 结构化阅读笔记（9 部分研究报告）
- 学习闪卡 / 测验题生成
- PDF 图表与章节关联

**学习模式：**
- Deck 模式 — 按主题分组的传统闪卡学习
- Paper 模式 — 按论文分组的阅读笔记 + 测验
- Gulp 模式 — 类似短视频的沉浸式刷卡学习

## 项目结构

```
gulp/
├── backend/        # FastAPI 后端服务
├── web/            # Next.js Web 客户端
├── ios/            # SwiftUI iOS 客户端
├── bruno/          # API 测试集合
└── docker-compose.yml
```

## 技术栈

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL, Redis, Alembic
- **Web:** Next.js 14, React, TypeScript, Tailwind CSS, Radix UI
- **iOS:** Swift, SwiftUI, iOS 17+
- **AI:** OpenAI 兼容 API（可配置 base URL），YAML 驱动的 Lens prompt 系统
- **算法:** FSRS（Free Spaced Repetition Scheduler）

## 本地开发

### 环境要求

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Xcode 15+（iOS 开发，可选）

### 启动基础设施

```bash
docker compose up -d
```

会启动 PostgreSQL、Redis 和 Qdrant。

### 启动后端

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 数据库迁移
alembic upgrade head

# 启动服务
uvicorn app.main:app --reload --port 8000
```

### 启动 Web 客户端

```bash
cd web
npm install
npm run dev
```

### 环境变量

复制 `backend/.env.example` 到 `backend/.env` 并填入：

| 变量 | 说明 |
|------|------|
| `DATABASE_URL` | PostgreSQL 连接串 |
| `REDIS_URL` | Redis 连接串 |
| `LM_API_KEY` | OpenAI 兼容 API Key |
| `LM_BASE_URL` | LM 端点（默认 OpenAI） |
| `LM_MODEL` | 模型名称 |
| `NOTION_CLIENT_ID` / `SECRET` | Notion OAuth（可选） |
| `SECRET_KEY` | JWT 签名密钥 |

### 运行测试

```bash
# 确保 PostgreSQL 已启动
docker compose up -d postgres

cd backend
venv/bin/pytest tests/
```

## License

MIT
