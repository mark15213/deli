from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import Snapshot, KnowledgeCard, KnowledgeBase, UserCardProgress, User
from app.schemas import (
    SnapshotResponse,
    KnowledgeCardResponse,
    CardReviewSubmit,
    SuccessResponse,
)
from app.dependencies import get_current_user
from datetime import datetime
import random

router = APIRouter(prefix="/gulp", tags=["gulp"])


@router.get("/stream", response_model=SuccessResponse[list[SnapshotResponse]])
async def get_gulp_stream(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取 Gulp 信息流 - 返回已处理的快照"""
    result = await db.execute(
        select(Snapshot)
        .where(
            Snapshot.user_id == current_user.id,
            Snapshot.status == "processed"
        )
        .order_by(Snapshot.added_at.desc())
        .limit(50)
    )
    snapshots = result.scalars().all()
    return SuccessResponse(data=[SnapshotResponse.model_validate(s) for s in snapshots])


@router.get("/quiz", response_model=SuccessResponse[list[KnowledgeCardResponse]])
async def get_quiz_cards(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取待复习的测验卡片 - 基于权重的简单算法"""

    # Get subscribed knowledge bases
    kb_result = await db.execute(
        select(KnowledgeBase.id)
        .where(
            KnowledgeBase.user_id == current_user.id,
            KnowledgeBase.is_subscribed == True
        )
    )
    kb_ids = [row[0] for row in kb_result.all()]

    if not kb_ids:
        return SuccessResponse(data=[], message="没有订阅的知识库")

    # Get cards from subscribed knowledge bases
    cards_result = await db.execute(
        select(KnowledgeCard)
        .where(KnowledgeCard.knowledge_base_id.in_(kb_ids))
    )
    all_cards = cards_result.scalars().all()

    if not all_cards:
        return SuccessResponse(data=[], message="没有可用的卡片")

    # Get user progress for these cards
    progress_result = await db.execute(
        select(UserCardProgress)
        .where(
            UserCardProgress.user_id == current_user.id,
            UserCardProgress.card_id.in_([c.id for c in all_cards])
        )
    )
    progress_map = {p.card_id: p for p in progress_result.scalars().all()}

    # Calculate weights and select cards
    weighted_cards = []
    for card in all_cards:
        progress = progress_map.get(card.id)
        if progress:
            weight = progress.weight
            # Skip mastered cards with low probability
            if progress.status == "mastered" and random.random() > 0.1:
                continue
        else:
            weight = 1.0  # New cards have default weight

        weighted_cards.append((card, weight))

    # Sort by weight (higher weight = more likely to appear)
    weighted_cards.sort(key=lambda x: x[1], reverse=True)

    # Select top cards (with some randomness)
    selected_count = min(12, len(weighted_cards))
    if selected_count > 5:
        # Take top 5 by weight, then random from the rest
        top_cards = [c for c, w in weighted_cards[:5]]
        remaining = [c for c, w in weighted_cards[5:]]
        random.shuffle(remaining)
        selected_cards = top_cards + remaining[:selected_count - 5]
    else:
        selected_cards = [c for c, w in weighted_cards[:selected_count]]

    random.shuffle(selected_cards)

    return SuccessResponse(
        data=[KnowledgeCardResponse.model_validate(c) for c in selected_cards],
        message=f"已为您准备 {len(selected_cards)} 张卡片"
    )


@router.post("/quiz/{card_id}/submit", response_model=SuccessResponse[dict])
async def submit_quiz(
    card_id: str,
    review_data: CardReviewSubmit,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """提交测验答案 - 与 /cards/{card_id}/review 相同的逻辑"""

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
        progress.weight = max(0.1, progress.weight * 0.8)
        if progress.correct_count >= 3:
            progress.status = "mastered"
        elif progress.review_count >= 1:
            progress.status = "learning"
    else:
        progress.weight = min(2.0, progress.weight * 1.5)
        progress.status = "learning"

    await db.commit()

    return SuccessResponse(
        data={
            "review_count": progress.review_count,
            "correct_count": progress.correct_count,
            "status": progress.status,
            "weight": progress.weight
        },
        message="答案已提交"
    )
