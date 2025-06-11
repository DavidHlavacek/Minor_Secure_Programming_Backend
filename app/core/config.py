from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # Application configuration
    app_name: str = "Minor Secure Programming API"
    debug: bool = False
    version: str = "0.1.0"
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Supabase configuration
    supabase_url: str
    supabase_key: str
    supabase_service_role_key: str | None = None
    
    # Security configuration
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS configuration
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"
    
    @property
    def allowed_origins_list(self) -> list[str]:
        """Convert comma-separated origins to list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in .env file


@lru_cache()
def get_settings():
    """
    Get cached settings instance with proper validation.
    """
    return Settings() 