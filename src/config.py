from pydantic_settings import BaseSettings
from pydantic import BaseModel, ConfigDict

class RedisConfig(BaseModel):
    host: str
    port: int

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    RESEND_API: str

    REDIS_HOST: str
    REDIS_PORT: int

    @property
    def redis(self) -> RedisConfig:
        return RedisConfig(host=self.REDIS_HOST, port=self.REDIS_PORT)

    model_config = ConfigDict(env_file=".env", extra="ignore")

settings = Settings()
