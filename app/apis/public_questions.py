from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.questions_model import Question
from app.schemas.questions_schema import QuestionPublicResponse
from uuid import UUID


public_router = APIRouter(prefix="/public/questions", tags=["Public Questions"])

@public_router.get("/qr/{qr_id}")
async def get_question_by_qr(qr_id: UUID, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Question)
        .where(Question.qr_id == qr_id)
        .options(
            selectinload(Question.options),
        )
    )
    question = await db.scalar(stmt)

    if not question:
        raise HTTPException(404, "Question not found")

    return QuestionPublicResponse.model_validate(question)