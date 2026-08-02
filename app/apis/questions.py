from io import BytesIO

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import StreamingResponse
from app.schemas.questions_schema import QuestionCreate, QuestionAdminResponse, QuestionUpdate
from app.core.settings import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.questions_model import QuestionOption, QuestionHint, Question
from app.core.db import get_db
import qrcode
from pathlib import Path
import shutil
from app.core.helpers import delete_local_file

q_router =  APIRouter(prefix="/admin/questions", tags=["Admin Questtions"])

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


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

    # Delete local files
    delete_local_file(question.qr_code_url)
    delete_local_file(question.image_url)

    await db.delete(question)
    await db.commit()
    return {"success": True, "message": "Question was deleted successfully."}

@q_router.post("/qr/{id}",status_code= 201)
async def generate_qr(id: int, db: AsyncSession = Depends(get_db)):
    question = await db.get(Question, id)
    if not question:
        raise HTTPException(404, "Question not found.")

    url = f"{settings.FE_BASE_URL}/q/{question.qr_id}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )

    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(
        fill_color="black",
        back_color="white",
    )

    folder = Path("/app/data/qr/questions")
    folder.mkdir(parents=True, exist_ok=True)

    path = folder / f"{id}.png"
    img.save(path, format="PNG")

    question.qr_code_url = f"/static/qr/questions/{id}.png"

    await db.commit()
    await db.refresh(question)
    return {
        "message": f"Generated QR Code for question {id}.",
        "qr_url": question.qr_code_url,
    }

@q_router.post("/{id}/image", status_code=201)
async def upload_question_image(
    id: int,
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    question = await db.get(Question, id)

    if question is None:
        raise HTTPException(404, "Question not found")

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(415,"Only JPG, PNG and WebP images are allowed")

    image.file.seek(0, 2)
    size = image.file.tell()
    image.file.seek(0)

    if size > MAX_IMAGE_SIZE:
        raise HTTPException(413, "Image must be 5 MB or smaller")

    extension = ALLOWED_IMAGE_TYPES[image.content_type]

    folder = Path(f"/app/data/questions")
    folder.mkdir(parents=True, exist_ok=True)

    path = folder / f"{id}{extension}"
    # Save without loading entire image into RAM
    with path.open("wb") as file:
        shutil.copyfileobj(image.file, file)

    question.image_url = f"/static/questions/{id}{extension}"
    await db.commit()
    await db.refresh(question)

    return {
            "message": f"Image saved for question {id}.",
            "qr_url": question.image_url,
        }
