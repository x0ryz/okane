from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_

from src.categories.models import Category
from src.categories.schemas import CreateCategory
from src.database import get_session
from src.auth.depends import read_user

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("/")
async def get_categories(session: AsyncSession = Depends(get_session), user = Depends(read_user)):
    query = await session.execute(select(Category).where(or_(Category.user_id == None, Category.user_id == user.id)))
    result = query.scalars().all()
    
    if not result:
        raise HTTPException(status_code=404, detail="Categories not found")

    return result

@router.post("/")
async def create_user_category(payload: CreateCategory, session: AsyncSession = Depends(get_session), user = Depends(read_user)):
    session.add(Category(user_id=user.id, name=payload.name))
    await session.commit()
    return {"message": "Category successfully created"}