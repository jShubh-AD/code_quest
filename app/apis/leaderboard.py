from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc
from app.core.db import get_db
from app.models.teams import Team
from app.models.submissison import Submission
from app.models.teams import Team

l_router = APIRouter(prefix="/admin/leaderboard", tags=["Admin Leaderboard"])

@l_router.get("/")
async def get_leaderboard(
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(
            Team.id,
            Team.team_name,
            func.coalesce(
                func.sum(Submission.points_awarded), 0
            ).label("total_points"),
            func.count(Submission.id).label("submission_count"),
            func.max(Submission.created_at).label("last_submission"),
        )
        .outerjoin(
            Submission,
            Submission.team_id == Team.id
        )
        .group_by(
            Team.id,
            Team.team_name,
        )
        .order_by(
            desc("total_points"),
            asc("last_submission"),
        )
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "rank": index,
            "team_id": row.id,
            "team_name": row.team_name,
            "total_points": row.total_points,
            "submission_count": row.submission_count,
            "last_submission": row.last_submission,
        }
        for index, row in enumerate(rows, start=1)
    ]