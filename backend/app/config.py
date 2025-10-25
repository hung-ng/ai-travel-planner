from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4.1-nano"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # PostgreSQL
    DATABASE_URL: str
    
    # ChromaDB
    CHROMA_URL: str
    
    # Redis (optional)
    REDIS_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True

    # Context Window
    CONTEXT_WINDOW_SIZE: int = 10
    CONTEXT_SUMMARIZE_THRESHOLD: int = 15
    
    #RAG Configurations
    RAG_TOP_K: int = 10
    RAG_SIMILARITY_THRESHOLD: float = 0.4
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()