from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from sqlalchemy import or_

from src.categories.models import Category
from src.categories.schemas import CategoryCreate, CategoryOut
from src.database import get_session
from src.auth.depends import read_user
from src.transactions.models import Transaction

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("/", response_model=list[CategoryOut])
async def get_categories(session: AsyncSession = Depends(get_session), user = Depends(read_user)):
    query = await session.execute(
        select(Category).where(
            or_(Category.user_id == None, Category.user_id == user.id)
        )
    )
    result = query.scalars().all()

    return result

@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_user_category(payload: CategoryCreate, session: AsyncSession = Depends(get_session), user = Depends(read_user)):
    query = select(Category).where(
        Category.name.ilike(payload.name.strip()),
        or_(
            Category.user_id == None,
            Category.user_id == user.id
        ),
    )

    result = await session.execute(query)

    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Category already exists")

    new_category = Category(user_id=user.id, name=payload.name.capitalize())
    session.add(new_category)
    await session.commit()
    await session.refresh(new_category)

    return new_category

@router.patch("/{category_id}", response_model=CategoryOut, responses={
    status.HTTP_403_FORBIDDEN: {"description": "You cannot edit global or other users' categories"},
    status.HTTP_404_NOT_FOUND: {"description": "Category does not exist"},
    status.HTTP_409_CONFLICT: {"description": "Category with this name already exists"},
})
async def update_category(category_id: int, payload: CategoryCreate, session: AsyncSession = Depends(get_session), user = Depends(read_user)):
    category = await session.get(Category, category_id)

    if not category:
        raise HTTPException(status_code=404, detail="Category does not exist")

    if category.user_id != user.id:
        raise HTTPException(status_code=403, detail="You cannot edit other users' categories")

    query = select(Category).where(
        Category.name.ilike(payload.name.strip()),
        Category.id != category_id,
        or_(
            Category.user_id == None,
            Category.user_id == user.id
        )
    )

    result = await session.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Category already exists")

    category.name = payload.name.capitalize()
    await session.commit()
    await session.refresh(category)

    return category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, session: AsyncSession = Depends(get_session), user = Depends(read_user)):
    category = await session.get(Category, category_id)

    if not category:
        raise HTTPException(status_code=404, detail="Category does not exist")

    if category.user_id != user.id:
        raise HTTPException(status_code=403, detail="You cannot edit other users' categories")

    query = select(Category).where(
        Category.name == "Інше",
        Category.user_id == None
    )
    result = await session.execute(query)
    other_category = result.scalar_one_or_none()

    stmt = (
        update(Transaction)
        .where(Transaction.category_id == category_id)
        .values(category_id=other_category.id)
    )

    await session.execute(stmt)

    await session.delete(category)
    await session.commit()

    return