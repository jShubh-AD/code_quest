from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.db import init_db
from contextlib import asynccontextmanager
from app.apis.questions import q_router
from app.apis.public_questions import public_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Code Quest API",
    version="v1.0.0",
    lifespan=lifespan,
)

app.include_router(q_router)
app.include_router(public_router)

@app.get("/")
def root():
    return {"status":"ok"}