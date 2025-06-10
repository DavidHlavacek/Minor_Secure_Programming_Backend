from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # TODO: Add application configuration
    app_name: str = "Minor Secure Programming API"
    debug: bool = False
    
    # TODO: Add Supabase configuration
    # supabase_url: str
    # supabase_key: str
    
    # TODO: Add database configuration
    # database_url: str
    
    # TODO: Add security configuration
    # secret_key: str
    # algorithm: str = "HS256"
    # access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    """
    Get cached settings instance.
    TODO: Implement proper settings caching and validation
    """
    return Settings() 