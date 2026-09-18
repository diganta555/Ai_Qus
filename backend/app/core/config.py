from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./storage/app.db"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    groq_api_key: str | None = None
    upload_dir: str = "./storage/uploads"
    jwt_secret_key: str = "change-this-to-a-real-random-secret-in-production"
    jwt_expire_minutes: int = 60 * 24 * 7

    class Config:
        env_file = ".env"

settings = Settings()