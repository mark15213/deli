# Backend

FastAPI 后端服务，提供 API、Quiz 生成、FSRS 调度等核心功能。

## 目录结构

```
backend/
├── app/
│   ├── api/           # API 路由
│   ├── core/          # 配置、安全、依赖
│   ├── models/        # SQLAlchemy 数据模型
│   ├── schemas/       # Pydantic 验证模型
│   ├── services/      # 业务逻辑层
│   ├── workers/       # Celery 异步任务
│   └── main.py        # 应用入口
├── alembic/           # 数据库迁移
├── tests/             # 测试用例
├── requirements.txt
└── Dockerfile
```

## 开发

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
uvicorn app.main:app --reload --port 8000

# 运行测试
pytest
```
