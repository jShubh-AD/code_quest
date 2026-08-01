from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from app.core.settings import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_local_session = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with async_local_session() as session:
        yield session

async def init_db():
    from app.models.questions_model import Question, QuestionHint, QuestionOption
    from app.models.teams import Teams
    from app.models.members import Member
    async with engine.begin() as con:
        await con.run_sync(Base.metadata.create_all)