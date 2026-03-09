from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update as sql_update
from app.database import get_db
from app.models import KnowledgeCard, KnowledgeBase, UserCardProgress, User
from app.schemas import (
    KnowledgeCardCreate,
    KnowledgeCardUpdate,
    KnowledgeCardResponse,
    CardReviewSubmit,
    SuccessResponse,
)
from app.dependencies import get_current_user
from datetime import datetime

router = APIRouter(prefix="/cards", tags=["cards"])


@router.get("", response_model=SuccessResponse[list[KnowledgeCardResponse]])
async def get_cards(
    knowledge_base_id: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(KnowledgeCard).join(KnowledgeBase).where(
        KnowledgeBase.user_id == current_user.id
    )

    if knowledge_base_id:
        query = query.where(KnowledgeCard.knowledge_base_id == knowledge_base_id)

    query = query.order_by(KnowledgeCard.created_at.desc())

    result = await db.execute(query)
    cards = result.scalars().all()
    return SuccessResponse(data=[KnowledgeCardResponse.model_validate(c) for c in cards])


@router.post("", response_model=SuccessResponse[KnowledgeCardResponse], status_code=status.HTTP_201_CREATED)
async def create_card(
    card_data: KnowledgeCardCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify KB ownership
    kb_result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.id == card_data.knowledge_base_id,
            KnowledgeBase.user_id == current_user.id
        )
    )
    kb = kb_result.scalar_one_or_none()

    if not kb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在")

    card = KnowledgeCard(**card_data.model_dump())
    db.add(card)

    # Update card count
    kb.card_count += 1

    await db.commit()
    await db.refresh(card)
    return SuccessResponse(data=KnowledgeCardResponse.model_validate(card), message="卡片创建成功")


@router.get("/{card_id}", response_model=SuccessResponse[KnowledgeCardResponse])
async def get_card(
    card_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(KnowledgeCard)
        .join(KnowledgeBase)
        .where(
            KnowledgeCard.id == card_id,
            KnowledgeBase.user_id == current_user.id
        )
    )
    card = result.scalar_one_or_none()

    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="卡片不存在")

    return SuccessResponse(data=KnowledgeCardResponse.model_validate(card))


@router.patch("/{card_id}", response_model=SuccessResponse[KnowledgeCardResponse])
async def update_card(
    card_id: str,
    card_data: KnowledgeCardUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(KnowledgeCard)
        .join(KnowledgeBase)
        .where(
            KnowledgeCard.id == card_id,
            KnowledgeBase.user_id == current_user.id
        )
    )
    card = result.scalar_one_or_none()

    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="卡片不存在")

    update_data = card_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(card, field, value)

    await db.commit()
    await db.refresh(card)
    return SuccessResponse(data=KnowledgeCardResponse.model_validate(card), message="卡片更新成功")


@router.delete("/{card_id}", response_model=SuccessResponse[dict])
async def delete_card(
    card_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(KnowledgeCard)
        .join(KnowledgeBase)
        .where(
            KnowledgeCard.id == card_id,
            KnowledgeBase.user_id == current_user.id
        )
    )
    card = result.scalar_one_or_none()

    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="卡片不存在")

    kb_id = card.knowledge_base_id

    await db.delete(card)

    # Update card count
    await db.execute(
        sql_update(KnowledgeBase)
        .where(KnowledgeBase.id == kb_id)
        .values(card_count=KnowledgeBase.card_count - 1)
    )

    await db.commit()
    return SuccessResponse(data={"id": card_id}, message="卡片删除成功")


@router.post("/{card_id}/review", response_model=SuccessResponse[dict])
async def review_card(
    card_id: str,
    review_data: CardReviewSubmit,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify card exists and user has access
    card_result = await db.execute(
        select(KnowledgeCard)
        .join(KnowledgeBase)
        .where(
            KnowledgeCard.id == card_id,
            KnowledgeBase.user_id == current_user.id
        )
    )
    card = card_result.scalar_one_or_none()

    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="卡片不存在")

    # Get or create progress
    progress_result = await db.execute(
        select(UserCardProgress).where(
            UserCardProgress.user_id == current_user.id,
            UserCardProgress.card_id == card_id
        )
    )
    progress = progress_result.scalar_one_or_none()

    if not progress:
        progress = UserCardProgress(
            user_id=current_user.id,
            card_id=card_id
        )
        db.add(progress)

    # Update progress
    progress.review_count += 1
    progress.last_reviewed_at = datetime.utcnow()

    if review_data.is_correct:
        progress.correct_count += 1
        progress.weight = max(0.1, progress.weight * 0.8)  # Decrease weight for correct answers
        if progress.correct_count >= 3:
            progress.status = "mastered"
        elif progress.review_count >= 1:
            progress.status = "learning"
    else:
        progress.weight = min(2.0, progress.weight * 1.5)  # Increase weight for incorrect answers
        progress.status = "learning"

    await db.commit()

    return SuccessResponse(
        data={
            "review_count": progress.review_count,
            "correct_count": progress.correct_count,
            "status": progress.status,
            "weight": progress.weight
        },
        message="复习记录已保存"
    )
