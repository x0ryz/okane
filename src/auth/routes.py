from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request

from src.auth.models import User, Session
from src.auth.schemas import UserRegister, UserLogin, Token
from src.auth.utils import get_password_hash, verify_password, create_access_token, create_refresh_token, get_token_hash
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

@router.post("/login", response_model=Token)
async def auth_user(payload: UserLogin, response: Response, session: AsyncSession = Depends(get_session)) -> Token:
    result = await session.execute(select(User).where(User.username == payload.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = await create_refresh_token(user_id=user.id, session=session)
    response.set_cookie(key="user_refresh_token", value=str(refresh_token), httponly=True, samesite="strict")
    return Token(access_token=access_token, token_type="bearer")

@router.post("/refresh", response_model=Token)
async def refresh_token(request: Request, response: Response, session: AsyncSession = Depends(get_session)) -> Token:
    refresh_token = request.cookies.get("user_refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is missing")
    
    session_query = await session.execute(select(Session).where(Session.token == get_token_hash(refresh_token)))
    session_data = session_query.scalar_one_or_none()

    if not session_data or session_data.expires_in < datetime.now(timezone.utc).timestamp():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
    
    user_query = await session.execute(select(User).where(User.id == session_data.user_id))
    user_data = user_query.scalar_one_or_none()

    if not user_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    await session.delete(session_data)
    
    access_token = create_access_token({"sub": str(user_data.id)})
    refresh_token = await create_refresh_token(user_id=user_data.id, session=session)
    response.set_cookie(key="user_refresh_token", value=str(refresh_token), httponly=True, samesite="strict")

    return Token(access_token=access_token, token_type="bearer")

@router.get("/logout")
async def logout_user(request: Request, response: Response, session: AsyncSession = Depends(get_session)):
    refresh_token = request.cookies.get("user_refresh_token")
    
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is missing")

    session_query = await session.execute(select(Session).where(Session.token == get_token_hash(refresh_token)))
    session_data = session_query.scalar_one_or_none()

    if session_data:
        await session.delete(session_data)
        await session.commit()

    response.delete_cookie("user_refresh_token")
    return {"message": "Logged out successfully"}