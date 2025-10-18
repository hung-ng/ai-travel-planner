from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # OpenAI
    OPENAI_API_KEY: str
    
    # Database
    DATABASE_URL: str = "postgresql://travelapp:devpassword123@localhost:5432/travel_planner"
    
    # ChromaDB
    CHROMA_URL: str = "http://localhost:8001"
    
    # Redis (optional)
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # API Settings (add these)
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True  # Match exact case in .env
        extra = "ignore"  # Ignore extra fields not in the model

settings = Settings()