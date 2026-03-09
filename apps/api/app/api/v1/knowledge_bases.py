from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import KnowledgeBase, KnowledgeCard, User
from app.schemas import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    KnowledgeCardResponse,
    SuccessResponse,
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/knowledge-bases", tags=["knowledge-bases"])


@router.get("", response_model=SuccessResponse[list[KnowledgeBaseResponse]])
async def get_knowledge_bases(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(KnowledgeBase)
        .where(KnowledgeBase.user_id == current_user.id)
        .order_by(KnowledgeBase.created_at.desc())
    )
    kbs = result.scalars().all()
    return SuccessResponse(data=[KnowledgeBaseResponse.model_validate(kb) for kb in kbs])


@router.post("", response_model=SuccessResponse[KnowledgeBaseResponse], status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(
    kb_data: KnowledgeBaseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    kb = KnowledgeBase(
        user_id=current_user.id,
        **kb_data.model_dump()
    )
    db.add(kb)
    await db.commit()
    await db.refresh(kb)
    return SuccessResponse(data=KnowledgeBaseResponse.model_validate(kb), message="知识库创建成功")


@router.get("/{kb_id}", response_model=SuccessResponse[KnowledgeBaseResponse])
async def get_knowledge_base(
    kb_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.user_id == current_user.id
        )
    )
    kb = result.scalar_one_or_none()

    if not kb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在")

    return SuccessResponse(data=KnowledgeBaseResponse.model_validate(kb))


@router.patch("/{kb_id}", response_model=SuccessResponse[KnowledgeBaseResponse])
async def update_knowledge_base(
    kb_id: str,
    kb_data: KnowledgeBaseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.user_id == current_user.id
        )
    )
    kb = result.scalar_one_or_none()

    if not kb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在")

    update_data = kb_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(kb, field, value)

    await db.commit()
    await db.refresh(kb)
    return SuccessResponse(data=KnowledgeBaseResponse.model_validate(kb), message="知识库更新成功")


@router.delete("/{kb_id}", response_model=SuccessResponse[dict])
async def delete_knowledge_base(
    kb_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.user_id == current_user.id
        )
    )
    kb = result.scalar_one_or_none()

    if not kb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在")

    await db.delete(kb)
    await db.commit()
    return SuccessResponse(data={"id": kb_id}, message="知识库删除成功")


@router.get("/{kb_id}/cards", response_model=SuccessResponse[list[KnowledgeCardResponse]])
async def get_knowledge_base_cards(
    kb_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify KB ownership
    kb_result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.user_id == current_user.id
        )
    )
    kb = kb_result.scalar_one_or_none()

    if not kb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在")

    # Get cards
    result = await db.execute(
        select(KnowledgeCard)
        .where(KnowledgeCard.knowledge_base_id == kb_id)
        .order_by(KnowledgeCard.created_at.desc())
    )
    cards = result.scalars().all()
    return SuccessResponse(data=[KnowledgeCardResponse.model_validate(c) for c in cards])
