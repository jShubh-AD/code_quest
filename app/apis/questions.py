from fastapi import APIRouter, HTTPException, Depends
from app.schemas.questions_schema import QuestionCreate, QuestionAdminResponse, QuestionUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.questions_model import QuestionOption, QuestionHint, Question
from app.core.db import get_db

q_router =  APIRouter(prefix="/admin/questions", tags=["Admin Questtions"])

@q_router.get("/")
async def get_questions(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Question)
            .options(
                selectinload(Question.hints),
                selectinload(Question.options),
            )
        )
    questions = (await db.scalars(stmt)).all()

    if not questions:
        raise HTTPException(404, "Question not found")
    return {
        "total": len(questions),
        "data": [QuestionAdminResponse.model_validate(q) for q in questions]
    }

@q_router.get("/{id}", status_code=200)
async def get_question_by_id(id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
            select(Question)
            .where(Question.id == id)
            .options(
                selectinload(Question.hints),
                selectinload(Question.options),
                )
            )
    question = await db.scalar(stmt)

    if not question:
        raise HTTPException(404, "Question not found")

    return QuestionAdminResponse.model_validate(question)

@q_router.post("/", status_code=201)
async def create_question(question: QuestionCreate, db: AsyncSession = Depends(get_db)):
    data = question.model_dump(exclude={"hints", "options"})
    db_question = Question(**data)

    db_question.hints = [
        QuestionHint(**hint.model_dump())
        for hint in question.hints
    ]

    db_question.options = [
        QuestionOption(**option.model_dump())
        for option in question.options
    ]

    db.add(db_question)
    await db.commit()
    await db.refresh(db_question)

    return db_question


@q_router.patch("/{id}")
async def update_question(id: int, payload: QuestionUpdate,db: AsyncSession = Depends(get_db)):
    question = await db.scalar(
        select(Question)
        .where(Question.id == id)
        .options(
            selectinload(Question.hints),
            selectinload(Question.options),
        )
    )

    if not question:
        raise HTTPException(404, "Question not found.")

    # Update question fields
    data = payload.model_dump(
        exclude={"hints", "options"},
        exclude_unset=True,
    )

    for key, value in data.items():
        setattr(question, key, value)

    # Replace hints
    if payload.hints is not None:
        question.hints.clear()
        question.hints.extend(
            QuestionHint(**hint.model_dump())
            for hint in payload.hints
        )

    # Replace options
    if payload.options is not None:
        question.options.clear()
        question.options.extend(
            QuestionOption(**option.model_dump())
            for option in payload.options
        )

    await db.commit()
    await db.refresh(question)

    return question

@q_router.delete("/{id}", status_code=200)
async def delete_question(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    question = await db.scalar(
        select(Question).where(Question.id == id)
    )

    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    await db.delete(question)
    await db.commit()
    return {"success": True, "message": "Question with deleted successfully."}