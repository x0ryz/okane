from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.transactions.models import Transaction
from src.transactions.schemas import CreateTransaction
from src.database import get_session
from src.auth.depends import read_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/")
async def create_transaction(payload: CreateTransaction, session: AsyncSession = Depends(get_session), user = Depends(read_user)):
    transaction = Transaction(**payload.model_dump(), user_id = user.id)

    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)

    return transaction