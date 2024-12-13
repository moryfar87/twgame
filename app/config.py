from pydantic_settings import BaseSettings
from pydantic import PostgresDsn


class Settings(BaseSettings):
    db_url: PostgresDsn = 'postgresql://student:student22112024@81.177.136.21:5432/twgame'
    secret_key: str = "12345"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
