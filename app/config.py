from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_url: str = "postgresql://student:student22112024@81.177.136.21:5432/twgame"
    secret_key: str = "your-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
