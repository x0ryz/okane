from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.models import User
from src.auth.schemas import UserRegister
from src.auth.utils import get_password_hash
from src.database import get_session

router = APIRouter(prefix="/auth", tags=["Authorization"])

@router.post("/register")
async def register_user(payload: UserRegister, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.username == payload.username))
    user = result.scalar_one_or_none()

    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is alredy exist")
    
    payload_dict = payload.model_dump()
    payload_dict["password"] = get_password_hash(payload.password)

    session.add(User(**payload_dict))
    await session.commit()
    
    return {"message": "User successfully registered"}