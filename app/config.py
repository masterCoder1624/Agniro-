import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Job Guidance Platform"
    VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = "sqlite:///./job_app.db"

    # Security
    SECRET_KEY: str = "SUPER_SECRET_KEY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # LLM API Keys
    OPENAI_API_KEY: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
