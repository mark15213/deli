from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Subscription, User
from app.schemas import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
    SuccessResponse,
    PaginatedResponse,
)
from app.dependencies import get_current_user
from app.utils.pagination import paginate

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("", response_model=SuccessResponse[list[SubscriptionResponse]])
async def get_subscriptions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == current_user.id)
        .order_by(Subscription.created_at.desc())
    )
    subscriptions = result.scalars().all()
    return SuccessResponse(data=[SubscriptionResponse.model_validate(s) for s in subscriptions])


@router.post("", response_model=SuccessResponse[SubscriptionResponse], status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    subscription = Subscription(
        user_id=current_user.id,
        **subscription_data.model_dump()
    )
    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)
    return SuccessResponse(data=SubscriptionResponse.model_validate(subscription), message="订阅源创建成功")


@router.get("/{subscription_id}", response_model=SuccessResponse[SubscriptionResponse])
async def get_subscription(
    subscription_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Subscription).where(
            Subscription.id == subscription_id,
            Subscription.user_id == current_user.id
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订阅源不存在")

    return SuccessResponse(data=SubscriptionResponse.model_validate(subscription))


@router.patch("/{subscription_id}", response_model=SuccessResponse[SubscriptionResponse])
async def update_subscription(
    subscription_id: str,
    subscription_data: SubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Subscription).where(
            Subscription.id == subscription_id,
            Subscription.user_id == current_user.id
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订阅源不存在")

    update_data = subscription_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(subscription, field, value)

    await db.commit()
    await db.refresh(subscription)
    return SuccessResponse(data=SubscriptionResponse.model_validate(subscription), message="订阅源更新成功")


@router.delete("/{subscription_id}", response_model=SuccessResponse[dict])
async def delete_subscription(
    subscription_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Subscription).where(
            Subscription.id == subscription_id,
            Subscription.user_id == current_user.id
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订阅源不存在")

    await db.delete(subscription)
    await db.commit()
    return SuccessResponse(data={"id": subscription_id}, message="订阅源删除成功")


@router.post("/{subscription_id}/fetch", response_model=SuccessResponse[dict])
async def fetch_subscription(
    subscription_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Subscription).where(
            Subscription.id == subscription_id,
            Subscription.user_id == current_user.id
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订阅源不存在")

    # TODO: 实现实际的抓取逻辑
    return SuccessResponse(data={"message": "抓取功能暂未实现，请手动添加内容"}, message="抓取请求已接收")
