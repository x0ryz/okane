from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from random import randint

from src.auth.models import User
from src.auth.schemas import UserRegister, UserLogin, AuthResponse, Token
from src.auth.utils import get_password_hash, verify_password, create_access_token, create_refresh_token, get_token_hash
from src.database import get_redis_client
from src.database import get_session

router = APIRouter(prefix="/auth", tags=["Authorization"])

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    responses={
        status.HTTP_409_CONFLICT: {"description": "User is already exist"}
})
async def register_user(payload: UserRegister, response: Response, session: AsyncSession = Depends(get_session),redis_client = Depends(get_redis_client)) -> Token:
    """
    Registers a new user in the system.

    - **email**: Must be unique.
    - **password**: Will be hashed using bcrypt before storage.
    """
    result = await session.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already exist")
    
    payload_dict = payload.model_dump()
    payload_dict["password"] = get_password_hash(payload.password)

    new_user = User(**payload_dict)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    verification_code = str(randint(100000, 999999))
    redis_key = f"verification:{new_user.email}"

    await redis_client.set(redis_key, verification_code, ex=300)

    return await _generate_auth_response(new_user, response, redis_client)

@router.post("/login", response_model=AuthResponse, summary="", responses={
    status.HTTP_401_UNAUTHORIZED: {"description": "Invalid credentials"}
})
async def auth_user(payload: UserLogin, response: Response, session: AsyncSession = Depends(get_session), redis_client = Depends(get_redis_client)) -> Token:
    """
    Authenticates a user and returns access/refresh tokens.

    If the authentication is successful:
    1. An **access token** (JWT) is returned in the response body.
    2. A **refresh token** is created and stored in Redis.
    """
    result = await session.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return await _generate_auth_response(user, response, redis_client)


async def _generate_auth_response(user, response: Response, redis_client):
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = await create_refresh_token(user_id=user.id, redis_client=redis_client)

    response.set_cookie(key="user_refresh_token", value=str(refresh_token), httponly=True, samesite="lax", secure=True)
    return AuthResponse(access_token=access_token, token_type="bearer", user=user)

@router.post("/refresh", response_model=Token, summary="Refresh access token", responses={
    status.HTTP_401_UNAUTHORIZED: {"description": "Refresh token is missing"},
    status.HTTP_404_NOT_FOUND: {"description": "User not found"},
})
async def update_refresh_token(request: Request, session: AsyncSession = Depends(get_session), redis_client = Depends(get_redis_client)) -> Token:
    """
    Endpoint to rotate access tokens without re-login.

    It validates the `user_refresh_token` cookie against the whitelist in Redis.
    If valid, a new short-lived **access token** is issued.
    """
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

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def logout_user(request: Request, response: Response, redis_client = Depends(get_redis_client)):
    """
    Performs a secure logout:

    1. Reads the refresh token from the cookie.
    2. Deletes the corresponding key from **Redis** (preventing reuse).
    3. Clears the `user_refresh_token` cookie from the browser.
    """
    refresh_token = request.cookies.get("user_refresh_token")

    if refresh_token:
        hash_token = get_token_hash(refresh_token)
        redis_key = f"refresh_token:{hash_token}"
        await redis_client.delete(redis_key)

    response.delete_cookie(
        key="user_refresh_token",
        httponly=True,
        samesite="lax",
        secure=True
    )

    return