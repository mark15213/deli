from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Snapshot, User
from app.schemas import (
    SnapshotCreate,
    SnapshotUpdate,
    SnapshotResponse,
    SuccessResponse,
    PaginatedResponse,
)
from app.dependencies import get_current_user
from app.utils.pagination import paginate
from datetime import datetime

router = APIRouter(prefix="/snapshots", tags=["snapshots"])


@router.get("", response_model=SuccessResponse[PaginatedResponse[SnapshotResponse]])
async def get_snapshots(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: str = Query(None, alias="status"),
    subscription_id: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Snapshot).where(Snapshot.user_id == current_user.id)

    if status_filter:
        query = query.where(Snapshot.status == status_filter)
    if subscription_id:
        query = query.where(Snapshot.subscription_id == subscription_id)

    query = query.order_by(Snapshot.added_at.desc())

    result = await paginate(query, db, page, limit)
    result["items"] = [SnapshotResponse.model_validate(s) for s in result["items"]]

    return SuccessResponse(data=result)


@router.post("", response_model=SuccessResponse[SnapshotResponse], status_code=status.HTTP_201_CREATED)
async def create_snapshot(
    snapshot_data: SnapshotCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    snapshot = Snapshot(
        user_id=current_user.id,
        **snapshot_data.model_dump()
    )
    db.add(snapshot)
    await db.commit()
    await db.refresh(snapshot)
    return SuccessResponse(data=SnapshotResponse.model_validate(snapshot), message="快照创建成功")


@router.get("/{snapshot_id}", response_model=SuccessResponse[SnapshotResponse])
async def get_snapshot(
    snapshot_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Snapshot).where(
            Snapshot.id == snapshot_id,
            Snapshot.user_id == current_user.id
        )
    )
    snapshot = result.scalar_one_or_none()

    if not snapshot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="快照不存在")

    return SuccessResponse(data=SnapshotResponse.model_validate(snapshot))


@router.patch("/{snapshot_id}", response_model=SuccessResponse[SnapshotResponse])
async def update_snapshot(
    snapshot_id: str,
    snapshot_data: SnapshotUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Snapshot).where(
            Snapshot.id == snapshot_id,
            Snapshot.user_id == current_user.id
        )
    )
    snapshot = result.scalar_one_or_none()

    if not snapshot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="快照不存在")

    update_data = snapshot_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(snapshot, field, value)

    if snapshot_data.status == "processed" and not snapshot.processed_at:
        snapshot.processed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(snapshot)
    return SuccessResponse(data=SnapshotResponse.model_validate(snapshot), message="快照更新成功")


@router.delete("/{snapshot_id}", response_model=SuccessResponse[dict])
async def delete_snapshot(
    snapshot_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Snapshot).where(
            Snapshot.id == snapshot_id,
            Snapshot.user_id == current_user.id
        )
    )
    snapshot = result.scalar_one_or_none()

    if not snapshot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="快照不存在")

    await db.delete(snapshot)
    await db.commit()
    return SuccessResponse(data={"id": snapshot_id}, message="快照删除成功")


@router.post("/{snapshot_id}/generate", response_model=SuccessResponse[dict])
async def generate_cards(
    snapshot_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Snapshot).where(
            Snapshot.id == snapshot_id,
            Snapshot.user_id == current_user.id
        )
    )
    snapshot = result.scalar_one_or_none()

    if not snapshot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="快照不存在")

    # TODO: 实现 AI 生成卡片逻辑
    return SuccessResponse(data={"message": "AI 生成功能暂未实现，请手动创建卡片"}, message="生成请求已接收")
