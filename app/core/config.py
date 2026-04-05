from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_env: str = "development"
    log_level: str = "info"
    
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    
    # Redis (for memory)
    redis_url: str = "redis://localhost:6379/0"
    
    # ChromaDB (for RAG)
    chroma_persist_dir: str = "./data/chroma"
    
    # Model paths (for local emotion/intent models if needed)
    emotion_model: str = "j-hartmann/emotion-english-distilroberta-base"
    intent_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Vector embedding model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
