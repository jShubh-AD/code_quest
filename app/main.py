from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.db import init_db
from contextlib import asynccontextmanager
from app.apis.questions import q_router
from app.apis.public_questions import public_router
from app.apis.teams import t_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Code Quest API",
    version="v1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/static",
    StaticFiles(directory="/app/data"),
    name="static",
)

app.include_router(q_router)
app.include_router(public_router)
app.include_router(t_router)

@app.get("/")
def root():
    return {"status":"ok"}