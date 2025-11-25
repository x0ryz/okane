from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.config import settings

engine = create_async_engine(settings.DATABASE_URL)

async_session = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()

async def get_session():
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
