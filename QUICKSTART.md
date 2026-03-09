# Gulp 项目快速启动指南

本指南帮助你快速启动 Gulp 项目的前后端服务。

## 前置要求

- Node.js 18+ 和 pnpm
- Python 3.11+
- Docker (用于 PostgreSQL 和 Redis)

## 1. 启动数据库服务

```bash
# 启动 PostgreSQL
docker run -d \
  --name gulp-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=gulp \
  -p 5432:5432 \
  postgres:16

# 启动 Redis
docker run -d \
  --name gulp-redis \
  -p 6379:6379 \
  redis:7
```

## 2. 启动后端 API

```bash
# 进入后端目录
cd apps/api

# 安装依赖
pip install -r requirements.txt

# 复制环境变量
cp .env.example .env

# 初始化数据库迁移
alembic init alembic

# 配置 alembic/env.py (参考 README.md)
# 然后创建并执行迁移
alembic revision --autogenerate -m "initial migration"
alembic upgrade head

# 启动服务
uvicorn app.main:app --reload --port 8000
```

后端 API 将在 http://localhost:8000 运行
API 文档: http://localhost:8000/docs

## 3. 启动前端应用

```bash
# 在项目根目录
pnpm install

# 启动 Web 应用
cd apps/web
pnpm dev
```

前端应用将在 http://localhost:3000 运行

## 4. 测试流程

### 4.1 注册和登录

1. 打开前端应用 http://localhost:3000
2. 注册一个新账号
3. 登录获取 JWT token

### 4.2 创建知识库

1. 进入 Knowledge Library 页面
2. 点击 "New Base" 创建知识库
3. 填写标题、描述、选择图标和颜色

### 4.3 创建知识卡片

1. 进入知识库详情页
2. 创建不同类型的卡片:
   - Flashcard (闪卡)
   - Single Choice (单选题)
   - Multiple Choice (多选题)

### 4.4 使用 Gulp 学习

1. 进入 Gulp Stream 页面
2. 点击 "Start Test" 开始测验
3. 系统会根据权重算法推荐卡片
4. 回答问题后提交,系统会调整卡片权重

### 4.5 管理订阅源和快照

1. 进入 Feed 页面
2. 添加订阅源 (RSS/网页链接)
3. 手动创建快照 (文章内容)
4. 在 Workspace 中编辑和生成卡片

## 5. API 测试 (使用 curl)

```bash
# 注册
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","username":"Test User"}'

# 登录
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  | jq -r '.data.access_token')

# 创建知识库
KB_ID=$(curl -X POST http://localhost:8000/api/v1/knowledge-bases \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"AI Architecture","description":"AI concepts","icon":"Database","color":"blue"}' \
  | jq -r '.data.id')

# 创建卡片
curl -X POST http://localhost:8000/api/v1/cards \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"knowledge_base_id\":\"$KB_ID\",\"card_type\":\"flashcard\",\"question\":\"What is a Transformer?\",\"answer\":\"A neural network architecture based on self-attention\",\"topic\":\"Deep Learning\"}"

# 获取测验卡片
curl -X GET http://localhost:8000/api/v1/gulp/quiz \
  -H "Authorization: Bearer $TOKEN"
```

## 6. 开发工具

### API 文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 数据库管理
```bash
# 连接 PostgreSQL
docker exec -it gulp-postgres psql -U postgres -d gulp

# 查看表
\dt

# 查看用户
SELECT * FROM users;
```

### 日志查看
```bash
# 后端日志
# uvicorn 会在终端输出日志

# 数据库日志
docker logs gulp-postgres

# Redis 日志
docker logs gulp-redis
```

## 7. 常见问题

### 数据库连接失败
- 确保 PostgreSQL 容器正在运行: `docker ps`
- 检查 .env 中的 DATABASE_URL 配置

### 前端无法连接后端
- 确保后端在 8000 端口运行
- 检查 apps/web/.env.local 中的 NEXT_PUBLIC_API_URL

### Alembic 迁移失败
- 确保已正确配置 alembic/env.py
- 删除 alembic/versions/ 中的旧迁移文件重新生成

## 8. 下一步

- [ ] 实现媒体文件上传功能
- [ ] 集成 AI (OpenAI/Claude) 自动生成卡片
- [ ] 实现 RSS/网页抓取功能
- [ ] 添加 SRS (间隔重复) 算法
- [ ] 部署到生产环境

## 9. 项目结构

```
gulp/
├── apps/
│   ├── api/          # FastAPI 后端
│   ├── web/          # Next.js 前端
│   └── ios/          # React Native iOS (未实现)
├── packages/         # 共享包
├── docs/             # 文档
│   └── plans/        # 设计文档和实现计划
└── README.md
```

## 10. 技术栈

**后端:**
- FastAPI (Web 框架)
- SQLAlchemy 2.0 (ORM)
- PostgreSQL (数据库)
- Redis (缓存)
- Alembic (迁移工具)
- JWT (认证)

**前端:**
- Next.js 16 (React 框架)
- TailwindCSS (样式)
- Radix UI (组件库)
- TipTap (富文本编辑器)

**开发工具:**
- pnpm (包管理)
- Turbo (Monorepo 构建)
- Docker (容器化)
