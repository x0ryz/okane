from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import APIRouter, Depends, HTTPException, status, Response

from src.auth.models import User
from src.auth.schemas import UserRegister, UserLogin
from src.auth.utils import get_password_hash, verify_password, create_access_token, create_refresh_token
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

@router.post("/login")
async def auth_user(payload: UserLogin, response: Response, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.username == payload.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.username})
    refresh_token = await create_refresh_token(user_id=user.id, session=session)
    response.set_cookie(key="user_refresh_token", value=str(refresh_token), httponly=True)
    return {"access_token": access_token}