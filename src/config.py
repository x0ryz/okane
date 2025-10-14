from pydantic_settings import BaseSettings
from pydantic import BaseModel

class RedisConfig(BaseModel):
    host: str
    port: int

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    REDIS_HOST: str
    REDIS_PORT: int

    @property
    def redis(self) -> RedisConfig:
        return RedisConfig(host=self.REDIS_HOST, port=self.REDIS_PORT)

    class Config:
        env_file = ".env"

settings = Settings()
