from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./database.db"
    GOOGLE_GEMINI_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()