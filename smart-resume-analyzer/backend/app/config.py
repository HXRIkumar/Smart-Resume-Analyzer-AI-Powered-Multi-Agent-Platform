"""Application configuration via pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # ─── Database ───
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/smart_resume_db"

    # ─── JWT ───
    SECRET_KEY: str = "your-super-secret-jwt-key-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ─── OAuth ───
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # ─── OpenAI ───
    OPENAI_API_KEY: str = ""

    # ─── File Uploads ───
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10

    # ─── Redis ───
    REDIS_URL: str = "redis://localhost:6379"

    # ─── General ───
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "http://localhost:5173"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


settings = Settings()
