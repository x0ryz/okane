from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request

from src.auth.models import User
from src.auth.schemas import UserRegister, UserLogin, Token
from src.auth.utils import get_password_hash, verify_password, create_access_token, create_refresh_token, get_token_hash
from src.auth.depends import get_redis_client
from src.database import get_session

router = APIRouter(prefix="/auth", tags=["Authorization"])

@router.post("/register")
async def register_user(payload: UserRegister, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already exist")
    
    payload_dict = payload.model_dump()
    payload_dict["password"] = get_password_hash(payload.password)

    session.add(User(**payload_dict))
    await session.commit()
    
    return {"message": "User successfully registered"}

@router.post("/login", response_model=Token)
async def auth_user(payload: UserLogin, response: Response, session: AsyncSession = Depends(get_session), redis_client = Depends(get_redis_client)) -> Token:
    result = await session.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = await create_refresh_token(user_id=user.id, redis_client=redis_client)
    response.set_cookie(key="user_refresh_token", value=str(refresh_token), httponly=True, samesite="strict")
    return Token(access_token=access_token, token_type="bearer")

@router.post("/refresh", response_model=Token)
async def update_refresh_token(request: Request, session: AsyncSession = Depends(get_session), redis_client = Depends(get_redis_client)) -> Token:
    refresh_token = request.cookies.get("user_refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is missing")
    
    hash_token = get_token_hash(refresh_token)  
    redis_key = f"refresh_token:{hash_token}"

    user_id = await redis_client.get(redis_key)
    
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
    
    user_query = await session.execute(select(User).where(User.id == int(user_id)))
    user_data = user_query.scalar_one_or_none()
    
    if not user_data:
        await redis_client.delete(redis_key)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # logger.info(f"Refresh token used and deleted for user {user_id}")
    
    access_token = create_access_token({"sub": str(user_data.id)})

    return Token(access_token=access_token, token_type="bearer")

@router.get("/logout")
async def logout_user(request: Request, response: Response, redis_client = Depends(get_redis_client)):
    refresh_token = request.cookies.get("user_refresh_token")
    
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is missing")

    hash_token = get_token_hash(refresh_token)
    redis_key = f"refresh_token:{hash_token}"

    await redis_client.delete(redis_key)

    response.delete_cookie("user_refresh_token")
    return {"message": "Logged out successfully"}