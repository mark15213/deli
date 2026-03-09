# Gulp 后端 API

基于 FastAPI + SQLAlchemy + PostgreSQL 的后端服务。

## 快速开始

### 1. 安装依赖

```bash
cd apps/api
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并修改配置:

```bash
cp .env.example .env
```

### 3. 启动数据库

使用 Docker 启动 PostgreSQL 和 Redis:

```bash
# PostgreSQL
docker run -d \
  --name gulp-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=gulp \
  -p 5432:5432 \
  postgres:16

# Redis
docker run -d \
  --name gulp-redis \
  -p 6379:6379 \
  redis:7
```

### 4. 初始化数据库

```bash
# 初始化 Alembic
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "initial migration"

# 执行迁移
alembic upgrade head
```

### 5. 启动服务

```bash
uvicorn app.main:app --reload --port 8000
```

API 文档将在 http://localhost:8000/docs 可用。

## API 端点

### 认证

- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/refresh` - 刷新 token
- `GET /api/v1/auth/me` - 获取当前用户信息

### 订阅源 (待实现)

- `GET /api/v1/subscriptions` - 获取所有订阅源
- `POST /api/v1/subscriptions` - 创建订阅源
- `GET /api/v1/subscriptions/:id` - 获取单个订阅源
- `PATCH /api/v1/subscriptions/:id` - 更新订阅源
- `DELETE /api/v1/subscriptions/:id` - 删除订阅源

### 快照 (待实现)

- `GET /api/v1/snapshots` - 获取所有快照
- `POST /api/v1/snapshots` - 创建快照
- `GET /api/v1/snapshots/:id` - 获取单个快照
- `PATCH /api/v1/snapshots/:id` - 更新快照
- `DELETE /api/v1/snapshots/:id` - 删除快照

### 知识库 (待实现)

- `GET /api/v1/knowledge-bases` - 获取所有知识库
- `POST /api/v1/knowledge-bases` - 创建知识库
- `GET /api/v1/knowledge-bases/:id` - 获取知识库详情
- `PATCH /api/v1/knowledge-bases/:id` - 更新知识库
- `DELETE /api/v1/knowledge-bases/:id` - 删除知识库

### 知识卡片 (待实现)

- `GET /api/v1/cards` - 获取所有卡片
- `POST /api/v1/cards` - 创建卡片
- `GET /api/v1/cards/:id` - 获取单个卡片
- `PATCH /api/v1/cards/:id` - 更新卡片
- `DELETE /api/v1/cards/:id` - 删除卡片
- `POST /api/v1/cards/:id/review` - 提交复习结果

### Gulp (待实现)

- `GET /api/v1/gulp/stream` - 获取信息流
- `GET /api/v1/gulp/quiz` - 获取测验卡片
- `POST /api/v1/gulp/quiz/:id/submit` - 提交测验答案

## 测试

使用 curl 测试认证端点:

```bash
# 注册
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","username":"Test User"}'

# 登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# 获取当前用户 (需要 token)
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 项目结构

```
apps/api/
├── app/
│   ├── api/v1/          # API 路由
│   ├── models/          # SQLAlchemy 模型
│   ├── schemas/         # Pydantic 模型
│   ├── utils/           # 工具函数
│   ├── config.py        # 配置
│   ├── database.py      # 数据库连接
│   ├── dependencies.py  # 依赖注入
│   └── main.py          # 应用入口
├── alembic/             # 数据库迁移
├── requirements.txt     # 依赖列表
└── .env.example         # 环境变量示例
```

## 开发状态

- [x] 项目基础设置
- [x] 数据模型实现
- [x] Pydantic Schemas
- [x] 认证 API
- [ ] 订阅源 API
- [ ] 快照 API
- [ ] 知识库 API
- [ ] 知识卡片 API
- [ ] Gulp API
- [ ] 媒体上传 API
