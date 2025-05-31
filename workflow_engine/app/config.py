# app/config.py
from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://puser:pPassword@localhost:5432/cv_builder"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # Security
    secret_key: str = "your-secret-key-here"
    allowed_origins: List[str] = ["*"]
    
    # Workflow Engine
    max_concurrent_workflows: int = 10
    default_step_timeout: int = 300
    handler_discovery_packages: List[str] = ["handlers"]
    
    # Cache
    cache_ttl_seconds: int = 3600
    
    class Config:
        env_file = ".env"

settings = Settings()
