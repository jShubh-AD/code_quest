from fastapi import APIRouter, HTTPException, Depends
from app.schemas.teams import TeamCreate, TeamResponse, TeamUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.db import get_db
from app.services.sheet_services import get_teams_registrations
from app.models.teams import Team
from pathlib import Path
import qrcode
from app.core.settings import settings
from app.services.smtp_service import send_registration_email
from uuid import UUID

t_router = APIRouter(prefix="/admin/teams", tags=["Admin Teams"])

@t_router.get("/")
async def get_teams(db: AsyncSession = Depends(get_db)):
    teams = (await db.scalars(select(Team))).all()
    if not teams:
        raise HTTPException(404, "Team not found.")
    
    return teams


@t_router.get("/{id}")
async def get_team_by_id(id: int, db: AsyncSession = Depends(get_db)):
    team = await db.get(Team, id)
    if not team:
        raise HTTPException(404, "Team not found.")
    
    return team

@t_router.get("/qr/{qr_id}")
async def get_teams_by_qr(qr_id: UUID, db: AsyncSession = Depends(get_db)):
    team = await db.scalar(
        select(Team).where(Team.qr_id == qr_id)
    )

    if not team:
        raise HTTPException(404, "Team not found.")
    
    return team

@t_router.patch("/{id}")
async def update_team_by_id(id: int,payload: TeamUpdate,db: AsyncSession = Depends(get_db)):
    team = await db.get(Team, id)
    if not team:
        raise HTTPException(404, "Team not found.")

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(team, field, value)

    await db.commit()
    await db.refresh(team)
    return team


    

@t_router.post("/import")
async def import_teams(db:AsyncSession = Depends(get_db)):
    registrations =  get_teams_registrations()

    teams = []
    for registration in registrations:
        team = Team(**registration.model_dump())
        db.add(team)
        teams.append(team)

    await db.commit()
    for team in teams:
        await db.refresh(team)

    return {
        "message": f"Imported {len(teams)} teams",
        "teams": teams,
    }

@t_router.post("/generate-qr")
async def generate_qr(db:AsyncSession = Depends(get_db)):
    teams = (await db.scalars(select(Team))).all()

    if not teams: 
        HTTPException(404, "No registered teams.")

    for team in teams:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )

        qr.add_data(team.qr_id)
        qr.make(fit=True)
        
        img = qr.make_image(
            fill_color="black",
            back_color="white",
        )

        folder = Path("/app/data/qr/teams")
        folder.mkdir(parents=True, exist_ok=True)
        
        path = folder / f"{team.id}.png"
        img.save(path, format="PNG")

        team.qr_url = f"/static/qr/teams/{team.id}.png"
        await db.commit()
        await db.refresh(team)

    return {
        "message": f"Imported {len(teams)} teams",
        "teams_qrs": [team.qr_url for team in teams],
    }

@t_router.post("/send-email/{id}")
async def send_email_by_id(id: int, db: AsyncSession = Depends(get_db)):
    team = await db.get(Team, id)
    if not team:
        raise HTTPException(404, "No teams found.")
    try:
        send_registration_email(team=team)
    except FileNotFoundError as e:
        raise HTTPException(400, e)
    except Exception as e:
        print(e)
        raise HTTPException(500, str(e))
    return {
        "message": f"Registration email sent to {team.leader_email}"
    }

    