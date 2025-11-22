from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from src.transactions.models import Transaction
from src.categories.models import Category
from src.auth.models import User
from src.transactions.schemas import TransactionCreate, TransactionOut
from src.database import get_session
from src.auth.depends import read_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/", response_model=TransactionOut)
async def create_transaction(
        payload: TransactionCreate,
        session: AsyncSession = Depends(get_session),
        user: User = Depends(read_user)
):
    query = select(Category).where(
        Category.id == payload.category_id,
        or_(
            Category.user_id == user.id,
            Category.user_id.is_(None)
        )
    )
    result = await session.execute(query)
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found or you don't have access to it"
        )

    new_transaction = Transaction(
        **payload.model_dump(),
        user_id=user.id
    )

    session.add(new_transaction)
    await session.commit()

    await session.refresh(new_transaction, attribute_names=["category"])

    return new_transaction

@router.get('/', response_model=list[TransactionOut])
async def get_transactions(
        transaction_type: Optional[Literal["expense", "income"]] = Query(None),
        session: AsyncSession = Depends(get_session),
        user: User = Depends(read_user)
):
    stmt = (select(Transaction)
        .options(joinedload(Transaction.category))
        .where(Transaction.user_id == user.id)
    )

    if transaction_type:
        stmt = stmt.where(Transaction.type == transaction_type)

    result = await session.execute(stmt)
    transactions = result.scalars().all()
    
    if not transactions:
        return []

    return transactions
