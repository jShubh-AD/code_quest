from fastapi import APIRouter, HTTPException
from app.schemas.teams import TeamCreate, TeamResponse, TeamUpdate

t_router = APIRouter(prefix="/admin/teams", tags=["Admin Teams"])

@t_router.get("/")
async def get_teams():
    return {"teams"}