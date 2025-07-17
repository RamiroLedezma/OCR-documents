import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import validator
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database settings
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', '3306'))
    DB_USER: str = os.getenv('DB_USER', 'root')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', '')
    DB_NAME: str = os.getenv('DB_NAME', 'davinchi')
    
    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    OPENAI_MAX_TOKENS: int = int(os.getenv('OPENAI_MAX_TOKENS', '1200'))
    
    # Security settings
    MAX_FILE_SIZE: int = int(os.getenv('MAX_FILE_SIZE', '10485760'))  # 10MB
    RATE_LIMIT_REQUESTS: int = int(os.getenv('RATE_LIMIT_REQUESTS', '100'))
    RATE_LIMIT_WINDOW: int = int(os.getenv('RATE_LIMIT_WINDOW', '3600'))  # 1 hour
    
    # Application settings
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    ENABLE_CACHE: bool = os.getenv('ENABLE_CACHE', 'True').lower() == 'true'
    CACHE_TTL: int = int(os.getenv('CACHE_TTL', '300'))  # 5 minutes
    
    @validator('OPENAI_API_KEY')
    def validate_openai_key(cls, v):
        if not v:
            raise ValueError('OPENAI_API_KEY is required')
        return v
    
    @validator('DB_PASSWORD')
    def validate_db_password(cls, v):
        if not v:
            raise ValueError('DB_PASSWORD is required')
        return v
    
    @property
    def database_url(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings() 