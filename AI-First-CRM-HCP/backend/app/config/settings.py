from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GROQ_API_KEY: str = ""
    MODEL_NAME: str = "llama-3.3-70b-versatile"
    DATABASE_URL: str = "sqlite:///./crm.db"

    class Config:
        env_file = ".env"


settings = Settings()
