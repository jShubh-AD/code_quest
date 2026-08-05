from fastapi import APIRouter, HTTPException, Depends
from app.core.db import get_db
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.teams import Team
from app.schemas.submission import SubmissionCreate
from app.models.submissison import Submission
from app.schemas.teams import VolunteerTeamResponse
from typing import Literal
from app.models.questions_model import Question

v_router = APIRouter(prefix="/volunteer", tags=["Volunteer Submissions"])

@v_router.get("/team/{qr_id}")
async def get_team_by_qr(
    qr_id: UUID, 
    db: AsyncSession = Depends(get_db)) -> VolunteerTeamResponse:
    stmt  = (
        select(Team)
        .where(Team.qr_id == qr_id)
        .options(
            selectinload(Team.submissions)
        )
    )

    team = await db.scalar(stmt)
    if not team:
        raise HTTPException(404, "team not found")

    response = VolunteerTeamResponse.model_validate(team)

    response.attempted_questions = len(team.submissions)
    response.total_points = sum(
        s.points_awarded or 0 for s in team.submissions
    )

    return response


@v_router.post("/team/submission/{qr_id}", status_code= 201)
async def save_submission(
    payload: SubmissionCreate,
    qr_id:  UUID,
    db: AsyncSession =  Depends(get_db)
):
    team = (await db.scalar(select(Team).where(Team.qr_id == qr_id)))

    if not team:
        raise HTTPException(404, "Team not found")

    # Team playing or not
    if team.status != "ongoing":
        raise HTTPException(400, "Team is not currently ongoing")

    # Question exists
    question = await db.scalar(
        select(Question).where(Question.id == payload.question_id)
    )

    if not question:
        raise HTTPException(404, "Question not found")

    # Already submitted
    existing_submission = await db.scalar(
        select(Submission).where(
            Submission.team_id == team.id,
            Submission.question_id == payload.question_id,
        )
    )

    if existing_submission:
        raise HTTPException(409, "Question already submitted by this team")

    if payload.points_awarded > question.points:
        raise HTTPException(400, "Awarded points cannot exceed question points")

    # Failed or Skipped question shouldn't receive points
    if payload.status != "solved" and payload.points_awarded > 0:
        raise HTTPException(400, "Failed or Skipped submission cannot receive points")

    submission = Submission(team_id=team.id, **payload.model_dump())

    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    return {
        "message": "Submission saved",
        "submission_id": submission,
    }

@v_router.post("/team/status/{qr_id}")
async def update_team_status(
    status: Literal["winner", "disqualified", "completed", "ongoing"], 
    qr_id:  UUID,
    db: AsyncSession =  Depends(get_db)):
    team = (await db.scalar(select(Team).where(Team.qr_id == qr_id)))

    if not team:
        raise HTTPException(404, "Team not found")
    team.status = status
    await db.commit()

    return {"message": "Team status updated"}

    