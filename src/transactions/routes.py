from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from src.transactions.models import Transaction
from src.categories.models import Category
from src.auth.models import User
from src.transactions.schemas import TransactionCreate, TransactionOut, TransactionUpdate
from src.database import get_session
from src.auth.depends import read_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])


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

@router.get("/{transaction_id}", response_model=TransactionOut)
async def get_transaction(transaction_id: int, session: AsyncSession = Depends(get_session), user: User = Depends(read_user)):
    query = (
        select(Transaction).where(Transaction.id == transaction_id)
        .options(joinedload(Transaction.category))
    )
    result = await session.execute(query)
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if not transaction.user_id == user.id:
        raise HTTPException(status_code=403, detail="You cannot access to other users' transactions")

    return transaction

@router.patch("/{transaction_id}", response_model=TransactionOut, responses={
    status.HTTP_403_FORBIDDEN: {"description": "You cannot edit other users' transactions"},
    status.HTTP_404_NOT_FOUND: {"description": "Transaction does not exist"},
})
async def update_transaction(transaction_id: int, payload: TransactionUpdate, session: AsyncSession = Depends(get_session), user: User = Depends(read_user)):
    query = (
        select(Transaction)
        .options(joinedload(Transaction.category))
        .where(Transaction.id == transaction_id)
    )
    result = await session.execute(query)
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if not transaction.user_id == user.id:
        raise HTTPException(status_code=403, detail="You cannot edit other users' transactions")


    if payload.category_id is not None:
        new_category = await session.get(Category, payload.category_id)

        if not new_category:
            raise HTTPException(status_code=404, detail="New category not found")

        if new_category.user_id is not None and new_category.user_id != user.id:
            raise HTTPException(status_code=403, detail="You cannot assign a category that belongs to another user")

    update_data = payload.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(transaction, key, value)

    await session.commit()
    result = await session.execute(
        select(Transaction)
        .options(joinedload(Transaction.category))
        .where(Transaction.id == transaction_id)
    )
    updated_transaction = result.scalar_one()

    return updated_transaction

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(transaction_id: int, session: AsyncSession = Depends(get_session), user: User = Depends(read_user)):
    transaction = await session.get(Transaction, transaction_id)

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if not transaction.user_id == user.id:
        raise HTTPException(status_code=403, detail="You cannot delete other users' transactions")

    await session.delete(transaction)
    await session.commit()

    return