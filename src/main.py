from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session

app = FastAPI()


@app.get("/")
async def read_root(session: AsyncSession = Depends(get_session)):
    await session.execute(text("SELECT 1"))
    return {"message": "DB connected"}