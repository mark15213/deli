# Deli

基于私有知识库的"第二大脑"训练场 - 将 Notion 笔记转化为具备间隔重复能力的 Quiz。

## 项目结构

```
deli/
├── backend/          # Python FastAPI 后端服务
├── ios/              # Swift/SwiftUI iOS 客户端
├── web/              # Next.js 管理端
├── docker/           # Docker 配置
└── docs/             # 项目文档
```

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 20+
- Xcode 15+ (iOS 开发)
- Docker & Docker Compose

### 本地开发

```bash
# 启动后端服务
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 启动 Web 管理端
cd web
npm install
npm run dev

# 运行测试
# 注意：测试依赖 pgvector 插件，需启动 Docker 容器
docker compose up -d postgres

# 运行后端测试
cd backend
venv/bin/pytest tests/
```

## 技术栈

- **Backend**: FastAPI, PostgreSQL, Redis, Celery
- **iOS**: Swift, SwiftUI, iOS 17+
- **Web**: Next.js, React, Tailwind CSS
- **AI**: LangChain, OpenAI API
- **Algorithm**: FSRS (Free Spaced Repetition Scheduler)

## License

MIT