# Gulp 后端实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现 Gulp 平台的完整后端 API，包括用户认证、订阅管理、快照管理、知识库管理、卡片管理和 Gulp 消费功能。

**Architecture:** 使用 FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL + Redis 构建 RESTful API。采用分层架构：API 层（路由）→ Service 层（业务逻辑）→ Model 层（数据访问）。JWT 认证保护所有需要授权的端点。

**Tech Stack:** FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL, Redis, JWT (python-jose), bcrypt (passlib)

---

## Task 1: 项目基础设置

**Files:**
- Create: `apps/api/app/__init__.py`
- Create: `apps/api/app/config.py`
- Create: `apps/api/app/database.py`
- Modify: `apps/api/requirements.txt`
- Create: `apps/api/.env.example`
- Create: `apps/api/alembic.ini`

**Step 1: 更新 requirements.txt**

```txt
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.25
alembic>=1.13.0
asyncpg>=0.29.0
pydantic>=2.6.0
pydantic-settings>=2.1.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.9
redis>=5.0.0
aiofiles>=23.2.1
```

**Step 2: 创建配置文件**

Create `apps/api/app/config.py`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/gulp"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001"]


settings = Settings()
```

**Step 3: 创建数据库连接**

Create `apps/api/app/database.py`:

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

**Step 4: 创建环境变量示例**

Create `apps/api/.env.example`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/gulp
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760
```

**Step 5: 初始化 Alembic**

Run: `cd apps/api && alembic init alembic`

**Step 6: 配置 Alembic**

Modify `apps/api/alembic/env.py` (在 `run_migrations_offline` 和 `run_migrations_online` 之前添加):

```python
from app.config import settings
from app.database import Base
from app.models import *  # Import all models

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("+asyncpg", ""))
target_metadata = Base.metadata
```

**Step 7: 提交**

```bash
git add apps/api/
git commit -m "feat(api): setup project foundation with FastAPI, SQLAlchemy, and Alembic

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 2: 数据模型实现

**Files:**
- Create: `apps/api/app/models/__init__.py`
- Create: `apps/api/app/models/user.py`
- Create: `apps/api/app/models/subscription.py`
- Create: `apps/api/app/models/snapshot.py`
- Create: `apps/api/app/models/knowledge_base.py`
- Create: `apps/api/app/models/knowledge_card.py`
- Create: `apps/api/app/models/user_card_progress.py`
- Create: `apps/api/app/models/media.py`

**Step 1: 创建 User 模型**

Create `apps/api/app/models/user.py`:

```python
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    snapshots: Mapped[list["Snapshot"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    knowledge_bases: Mapped[list["KnowledgeBase"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    media: Mapped[list["Media"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    card_progress: Mapped[list["UserCardProgress"]] = relationship(back_populates="user", cascade="all, delete-orphan")
```

**Step 2: 创建 Subscription 模型**

Create `apps/api/app/models/subscription.py`:

```python
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class FrequencyEnum(str, enum.Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MANUAL = "Manual"


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    frequency: Mapped[FrequencyEnum] = mapped_column(SQLEnum(FrequencyEnum), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    last_fetched_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="subscriptions")
    snapshots: Mapped[list["Snapshot"]] = relationship(back_populates="subscription", cascade="all, delete-orphan")
```

**Step 3: 创建 Snapshot 模型**

Create `apps/api/app/models/snapshot.py`:

```python
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class ContentFormatEnum(str, enum.Enum):
    MARKDOWN = "markdown"
    HTML = "html"


class SnapshotStatusEnum(str, enum.Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    ARCHIVED = "archived"


class Snapshot(Base):
    __tablename__ = "snapshots"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    subscription_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("subscriptions.id"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str | None] = mapped_column(Text)
    content_format: Mapped[ContentFormatEnum] = mapped_column(SQLEnum(ContentFormatEnum), default=ContentFormatEnum.MARKDOWN)
    images: Mapped[dict | None] = mapped_column(JSON)
    metadata: Mapped[dict | None] = mapped_column(JSON)
    status: Mapped[SnapshotStatusEnum] = mapped_column(SQLEnum(SnapshotStatusEnum), default=SnapshotStatusEnum.PENDING, index=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="snapshots")
    subscription: Mapped["Subscription | None"] = relationship(back_populates="snapshots")
    knowledge_cards: Mapped[list["KnowledgeCard"]] = relationship(back_populates="snapshot")
```

**Step 4: 创建 KnowledgeBase 模型**

Create `apps/api/app/models/knowledge_base.py`:

```python
from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid
from app.database import Base


class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    icon: Mapped[str] = mapped_column(String(50), default="Database")
    color: Mapped[str] = mapped_column(String(50), default="blue")
    is_subscribed: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    card_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="knowledge_bases")
    cards: Mapped[list["KnowledgeCard"]] = relationship(back_populates="knowledge_base", cascade="all, delete-orphan")
```

**Step 5: 创建 KnowledgeCard 模型**

Create `apps/api/app/models/knowledge_card.py`:

```python
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class CardTypeEnum(str, enum.Enum):
    FLASHCARD = "flashcard"
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"


class KnowledgeCard(Base):
    __tablename__ = "knowledge_cards"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    knowledge_base_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_bases.id"), nullable=False, index=True)
    snapshot_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("snapshots.id"), index=True)
    card_type: Mapped[CardTypeEnum] = mapped_column(SQLEnum(CardTypeEnum), nullable=False, index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str | None] = mapped_column(Text)
    explanation: Mapped[str | None] = mapped_column(Text)
    options: Mapped[list | None] = mapped_column(JSON)
    correct_answer: Mapped[int | list | None] = mapped_column(JSON)
    topic: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    knowledge_base: Mapped["KnowledgeBase"] = relationship(back_populates="cards")
    snapshot: Mapped["Snapshot | None"] = relationship(back_populates="knowledge_cards")
    user_progress: Mapped[list["UserCardProgress"]] = relationship(back_populates="card", cascade="all, delete-orphan")
```

**Step 6: 创建 UserCardProgress 模型**

Create `apps/api/app/models/user_card_progress.py`:

```python
from sqlalchemy import Float, Integer, DateTime, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class ProgressStatusEnum(str, enum.Enum):
    NEW = "new"
    LEARNING = "learning"
    MASTERED = "mastered"


class UserCardProgress(Base):
    __tablename__ = "user_card_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "card_id", name="uq_user_card"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    card_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_cards.id"), nullable=False, index=True)
    status: Mapped[ProgressStatusEnum] = mapped_column(SQLEnum(ProgressStatusEnum), default=ProgressStatusEnum.NEW)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    weight: Mapped[float] = mapped_column(Float, default=1.0, index=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="card_progress")
    card: Mapped["KnowledgeCard"] = relationship(back_populates="user_progress")
```

**Step 7: 创建 Media 模型**

Create `apps/api/app/models/media.py`:

```python
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid
from app.database import Base


class Media(Base):
    __tablename__ = "media"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="media")
```

**Step 8: 创建 models __init__.py**

Create `apps/api/app/models/__init__.py`:

```python
from app.models.user import User
from app.models.subscription import Subscription, FrequencyEnum
from app.models.snapshot import Snapshot, ContentFormatEnum, SnapshotStatusEnum
from app.models.knowledge_base import KnowledgeBase
from app.models.knowledge_card import KnowledgeCard, CardTypeEnum
from app.models.user_card_progress import UserCardProgress, ProgressStatusEnum
from app.models.media import Media

__all__ = [
    "User",
    "Subscription",
    "FrequencyEnum",
    "Snapshot",
    "ContentFormatEnum",
    "SnapshotStatusEnum",
    "KnowledgeBase",
    "KnowledgeCard",
    "CardTypeEnum",
    "UserCardProgress",
    "ProgressStatusEnum",
    "Media",
]
```

**Step 9: 创建数据库迁移**

Run: `cd apps/api && alembic revision --autogenerate -m "create initial tables"`

**Step 10: 提交**

```bash
git add apps/api/app/models/
git add apps/api/alembic/
git commit -m "feat(api): implement SQLAlchemy models for all entities

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 3: Pydantic Schemas

**Files:**
- Create: `apps/api/app/schemas/__init__.py`
- Create: `apps/api/app/schemas/auth.py`
- Create: `apps/api/app/schemas/subscription.py`
- Create: `apps/api/app/schemas/snapshot.py`
- Create: `apps/api/app/schemas/knowledge_base.py`
- Create: `apps/api/app/schemas/knowledge_card.py`
- Create: `apps/api/app/schemas/media.py`
- Create: `apps/api/app/schemas/common.py`

**Step 1: 创建通用 schemas**

Create `apps/api/app/schemas/common.py`:

```python
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    message: str = "操作成功"


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    limit: int
    pages: int
```

**Step 2: 创建认证 schemas**

Create `apps/api/app/schemas/auth.py`:

```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
import uuid


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    username: str | None = Field(None, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    username: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

**Step 3: 创建订阅 schemas**

Create `apps/api/app/schemas/subscription.py`:

```python
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
import uuid
from app.models.subscription import FrequencyEnum


class SubscriptionCreate(BaseModel):
    title: str = Field(max_length=255)
    url: str = Field(max_length=500)
    frequency: FrequencyEnum


class SubscriptionUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)
    url: str | None = Field(None, max_length=500)
    frequency: FrequencyEnum | None = None
    is_active: bool | None = None


class SubscriptionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    url: str
    frequency: FrequencyEnum
    is_active: bool
    last_fetched_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubscriptionWithSnapshots(SubscriptionResponse):
    unread_count: int = 0
    snapshots: list["SnapshotResponse"] = []
```

**Step 4: 创建快照 schemas**

Create `apps/api/app/schemas/snapshot.py`:

```python
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from app.models.snapshot import ContentFormatEnum, SnapshotStatusEnum


class SnapshotCreate(BaseModel):
    title: str = Field(max_length=500)
    url: str = Field(max_length=1000)
    summary: str | None = None
    content: str | None = None
    content_format: ContentFormatEnum = ContentFormatEnum.MARKDOWN
    images: dict | None = None
    metadata: dict | None = None
    subscription_id: uuid.UUID | None = None


class SnapshotUpdate(BaseModel):
    title: str | None = Field(None, max_length=500)
    summary: str | None = None
    content: str | None = None
    content_format: ContentFormatEnum | None = None
    images: dict | None = None
    metadata: dict | None = None
    status: SnapshotStatusEnum | None = None


class SnapshotResponse(BaseModel):
    id: uuid.UUID
    subscription_id: uuid.UUID | None
    user_id: uuid.UUID
    title: str
    url: str
    summary: str | None
    content: str | None
    content_format: ContentFormatEnum
    images: dict | None
    metadata: dict | None
    status: SnapshotStatusEnum
    added_at: datetime
    processed_at: datetime | None

    class Config:
        from_attributes = True
```

**Step 5: 创建知识库 schemas**

Create `apps/api/app/schemas/knowledge_base.py`:

```python
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class KnowledgeBaseCreate(BaseModel):
    title: str = Field(max_length=255)
    description: str | None = None
    icon: str = Field(default="Database", max_length=50)
    color: str = Field(default="blue", max_length=50)
    is_subscribed: bool = True


class KnowledgeBaseUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)
    description: str | None = None
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, max_length=50)
    is_subscribed: bool | None = None


class KnowledgeBaseResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: str | None
    icon: str
    color: str
    is_subscribed: bool
    card_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

**Step 6: 创建知识卡片 schemas**

Create `apps/api/app/schemas/knowledge_card.py`:

```python
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from app.models.knowledge_card import CardTypeEnum


class KnowledgeCardCreate(BaseModel):
    knowledge_base_id: uuid.UUID
    snapshot_id: uuid.UUID | None = None
    card_type: CardTypeEnum
    question: str
    answer: str | None = None
    explanation: str | None = None
    options: list[str] | None = None
    correct_answer: int | list[int] | None = None
    topic: str | None = Field(None, max_length=100)


class KnowledgeCardUpdate(BaseModel):
    question: str | None = None
    answer: str | None = None
    explanation: str | None = None
    options: list[str] | None = None
    correct_answer: int | list[int] | None = None
    topic: str | None = Field(None, max_length=100)


class KnowledgeCardResponse(BaseModel):
    id: uuid.UUID
    knowledge_base_id: uuid.UUID
    snapshot_id: uuid.UUID | None
    card_type: CardTypeEnum
    question: str
    answer: str | None
    explanation: str | None
    options: list[str] | None
    correct_answer: int | list[int] | None
    topic: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CardReviewSubmit(BaseModel):
    is_correct: bool
    time_spent: int | None = None  # seconds
```

**Step 7: 创建媒体 schemas**

Create `apps/api/app/schemas/media.py`:

```python
from pydantic import BaseModel
from datetime import datetime
import uuid


class MediaResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    file_name: str
    file_url: str
    file_type: str
    file_size: int
    uploaded_at: datetime

    class Config:
        from_attributes = True
```

**Step 8: 创建 schemas __init__.py**

Create `apps/api/app/schemas/__init__.py`:

```python
from app.schemas.common import SuccessResponse, ErrorResponse, PaginatedResponse
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, TokenRefresh, UserResponse
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse, SubscriptionWithSnapshots
from app.schemas.snapshot import SnapshotCreate, SnapshotUpdate, SnapshotResponse
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseResponse
from app.schemas.knowledge_card import KnowledgeCardCreate, KnowledgeCardUpdate, KnowledgeCardResponse, CardReviewSubmit
from app.schemas.media import MediaResponse

__all__ = [
    "SuccessResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "UserRegister",
    "UserLogin",
    "TokenResponse",
    "TokenRefresh",
    "UserResponse",
    "SubscriptionCreate",
    "SubscriptionUpdate",
    "SubscriptionResponse",
    "SubscriptionWithSnapshots",
    "SnapshotCreate",
    "SnapshotUpdate",
    "SnapshotResponse",
    "KnowledgeBaseCreate",
    "KnowledgeBaseUpdate",
    "KnowledgeBaseResponse",
    "KnowledgeCardCreate",
    "KnowledgeCardUpdate",
    "KnowledgeCardResponse",
    "CardReviewSubmit",
    "MediaResponse",
]
```

**Step 9: 提交**

```bash
git add apps/api/app/schemas/
git commit -m "feat(api): implement Pydantic schemas for request/response validation

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 4: 认证工具和依赖

**Files:**
- Create: `apps/api/app/utils/__init__.py`
- Create: `apps/api/app/utils/security.py`
- Create: `apps/api/app/utils/pagination.py`
- Create: `apps/api/app/dependencies.py`

**Step 1: 创建安全工具**

Create `apps/api/app/utils/security.py`:

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
```

**Step 2: 创建分页工具**

Create `apps/api/app/utils/pagination.py`:

```python
from math import ceil
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


async def paginate(query, session: AsyncSession, page: int = 1, limit: int = 20):
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await session.scalar(count_query)

    # Calculate pagination
    pages = ceil(total / limit) if total > 0 else 0
    offset = (page - 1) * limit

    # Get items
    items_query = query.limit(limit).offset(offset)
    result = await session.execute(items_query)
    items = result.scalars().all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
    }
```

**Step 3: 创建依赖注入**

Create `apps/api/app/dependencies.py`:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User
from app.utils.security import decode_token
import uuid

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID",
        )

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
```

**Step 4: 提交**

```bash
git add apps/api/app/utils/ apps/api/app/dependencies.py
git commit -m "feat(api): implement security utilities and authentication dependencies

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 5: 认证 API 实现

**Files:**
- Create: `apps/api/app/api/__init__.py`
- Create: `apps/api/app/api/v1/__init__.py`
- Create: `apps/api/app/api/v1/auth.py`
- Modify: `apps/api/app/main.py`

**Step 1: 创建认证路由**

Create `apps/api/app/api/v1/auth.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User
from app.schemas import (
    UserRegister,
    UserLogin,
    TokenResponse,
    TokenRefresh,
    UserResponse,
    SuccessResponse,
)
from app.utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=SuccessResponse[UserResponse])
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        username=user_data.username,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return SuccessResponse(data=UserResponse.model_validate(user), message="注册成功")


@router.post("/login", response_model=SuccessResponse[TokenResponse])
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    # Find user
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Create tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return SuccessResponse(
        data=TokenResponse(access_token=access_token, refresh_token=refresh_token),
        message="登录成功",
    )


@router.post("/refresh", response_model=SuccessResponse[TokenResponse])
async def refresh_token(token_data: TokenRefresh, db: AsyncSession = Depends(get_db)):
    payload = decode_token(token_data.refresh_token)

    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Create new tokens
    access_token = create_access_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})

    return SuccessResponse(
        data=TokenResponse(access_token=access_token, refresh_token=refresh_token),
        message="Token 刷新成功",
    )


@router.get("/me", response_model=SuccessResponse[UserResponse])
async def get_me(current_user: User = Depends(get_current_user)):
    return SuccessResponse(data=UserResponse.model_validate(current_user))
```

**Step 2: 创建 API v1 __init__.py**

Create `apps/api/app/api/v1/__init__.py`:

```python
from fastapi import APIRouter
from app.api.v1 import auth

api_router = APIRouter(prefix="/v1")

api_router.include_router(auth.router)
```

**Step 3: 更新 main.py**

Modify `apps/api/app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import api_router

app = FastAPI(title="Gulp API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "Welcome to Gulp API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

**Step 4: 提交**

```bash
git add apps/api/app/api/ apps/api/app/main.py
git commit -m "feat(api): implement authentication endpoints (register, login, refresh, me)

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

由于实现计划非常长，我将继续完成剩余的 API 实现部分。让我继续编写...
