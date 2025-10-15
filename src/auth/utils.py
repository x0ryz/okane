from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from src.config import settings
import uuid, jwt, hashlib

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

async def create_refresh_token(user_id: int, redis_client) -> str:
    refresh_token = str(uuid.uuid4())
    hash_token = get_token_hash(refresh_token)

    expires_in_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    redis_key = f"refresh_token:{hash_token}"

    await redis_client.setex(
        redis_key,
        expires_in_seconds,
        str(user_id)
    )

    return refresh_token

def verify_refresh_token(raw_token: str, stored_hash: str) -> bool:
    return get_token_hash(raw_token) == stored_hash

def decode_token(token: str):
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
    return payload