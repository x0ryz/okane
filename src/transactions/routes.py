from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.transactions.models import Transaction
from src.transactions.schemas import TransactionCreate, TransactionDetail, TransactionOut
from src.database import get_session
from src.auth.depends import read_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/", response_model=TransactionDetail)
async def create_transaction(payload: TransactionCreate, session: AsyncSession = Depends(get_session), user = Depends(read_user)):
    transaction = Transaction(**payload.model_dump(), user_id = user.id)

    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)

    return transaction

@router.get('/', response_model=list[TransactionOut])
async def get_transactions(session: AsyncSession = Depends(get_session), user = Depends(read_user)):
    query = await session.execute(select(Transaction).where(Transaction.user_id == user.id))
    result = query.scalars().all()
    
    if not result:
        raise HTTPException(status_code=404, detail="Transactions not found")

    return result

@router.get("/{transaction_id}", response_model=TransactionDetail)
async def get_transaction_by_id(transaction_id: int, session: AsyncSession = Depends(get_session), user = Depends(read_user)):
    query = await session.execute(select(Transaction).where(Transaction.id == transaction_id), Transaction.user_id == user.id)
    result = query.scalar_one_or_none()

    if not result:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return result

@router.delete("/{transaction_id}")
async def delete_transaction_by_id(transaction_id: int, session: AsyncSession = Depends(get_session), user = Depends(read_user)):
    query = await session.execute(select(Transaction).where(Transaction.id == transaction_id), Transaction.user_id == user.id)
    result = query.scalar_one_or_none()

    if result:
        await session.delete(result)
        await session.commit()
    else:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return {"message": "Transaction successfully deleted"}