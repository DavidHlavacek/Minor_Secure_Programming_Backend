from supabase import create_client, Client
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Supabase client wrapper for database operations.
    """
    
    def __init__(self):
        self.client: Client = None
        self._settings = None
        
    async def connect(self):
        """
        Initialize Supabase connection.
        """
        try:
            self._settings = get_settings()
            self.client = create_client(
                self._settings.supabase_url, 
                self._settings.supabase_key
            )
            logger.info("Successfully connected to Supabase")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            raise
        
    async def disconnect(self):
        """
        Close Supabase connection.
        Note: Supabase Python client doesn't require explicit disconnection
        """
        self.client = None
        logger.info("Disconnected from Supabase")
        
    async def health_check(self) -> bool:
        """
        Check database connectivity by testing a simple query.
        """
        try:
            if not self.client:
                return False
                
            # Test connection with a simple query to auth.users
            response = self.client.auth.get_session()
            return True
        except Exception as e:
            logger.error(f"Supabase health check failed: {e}")
            return False
    
    def get_client(self) -> Client:
        """
        Get the Supabase client instance.
        """
        if not self.client:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.client


# Global database instance
db = SupabaseClient()


async def get_database() -> SupabaseClient:
    """
    Dependency to get database instance.
    """
    return db


async def init_db():
    """
    Initialize database connection and verify tables.
    """
    try:
        await db.connect()
        
        # Verify connection with health check
        if await db.health_check():
            logger.info("Database initialization completed successfully")
        else:
            logger.warning("Database connection established but health check failed")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def close_db():
    """
    Close database connections.
    """
    await db.disconnect()