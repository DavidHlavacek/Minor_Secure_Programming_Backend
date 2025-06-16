from supabase import create_client, Client
from app.core.config import get_settings
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List, Union, Callable, AsyncGenerator
import logging
from functools import wraps
from fastapi import Depends, HTTPException, status

# Initialize logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Try to import Supabase, but don't fail if it's not available
try:
    SUPABASE_AVAILABLE = True
except ImportError:
    logger.warning("Supabase client not available, falling back to mock database")
    SUPABASE_AVAILABLE = False

# Import our mock database as fallback
from .mock_db import mock_db

class DatabaseClient:
    """
    Abstract base class for database clients, whether Supabase or mock.
    """
    async def select(self, table: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        raise NotImplementedError("Subclass must implement this method")
        
    async def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Subclass must implement this method")
        
    async def update(self, table: str, id_value: str, data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Subclass must implement this method")
        
    async def delete(self, table: str, id_value: str) -> bool:
        raise NotImplementedError("Subclass must implement this method")
        
    async def get_by_id(self, table: str, id_value: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError("Subclass must implement this method")

class SupabaseClient(DatabaseClient):
    """
    Wrapper for Supabase client to manage database connections.
    """
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.client: Optional[Client] = None

    async def connect(self) -> 'SupabaseClient':
        """
        Create a connection to Supabase or return existing connection.
        """
        if not self.client:
            if not self.url or not self.key:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
            self.client = create_client(self.url, self.key)
        return self

    async def connect_service_role(self) -> 'SupabaseClient':
        """
        Create a connection with service_role key for admin operations.
        """
        if not self.url or not self.service_role_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        self.client = create_client(self.url, self.service_role_key)
        return self

    async def disconnect(self) -> None:
        """
        Close the connection to Supabase.
        """
        # Supabase Python client doesn't have a close method,
        # but we keep this for future compatibility
        self.client = None
        
    async def select(self, table: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Select records from a table with optional filters"""
        query = self.client.table(table).select("*")
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        # Supabase client doesn't use await for the execute method
        response = query.execute()
        return response.data
    
    async def get_by_id(self, table: str, id_value: str) -> Optional[Dict[str, Any]]:
        """Get a record by ID"""
        response = self.client.table(table).select("*").eq("id", id_value).limit(1).execute()
        return response.data[0] if response.data else None
        
    async def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a record into a table"""
        response = self.client.table(table).insert(data).execute()
        return response.data[0] if response.data else {}
    
    async def update(self, table: str, id_value: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a record by ID"""
        response = self.client.table(table).update(data).eq("id", id_value).execute()
        return response.data[0] if response.data else {}
    
    async def delete(self, table: str, id_value: str) -> bool:
        """Delete a record by ID"""
        response = self.client.table(table).delete().eq("id", id_value).execute()
        return len(response.data) > 0

class MockClientWrapper(DatabaseClient):
    """
    Wrapper for mock database that follows the same interface as SupabaseClient.
    """
    def __init__(self):
        self.db = mock_db
        
    async def connect(self) -> 'MockClientWrapper':
        """Mock connect method"""
        return self
        
    async def connect_service_role(self) -> 'MockClientWrapper':
        """Mock service role connect method"""
        return self
        
    async def disconnect(self) -> None:
        """Mock disconnect method"""
        pass
    
    async def select(self, table: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Select records from mock database"""
        return await self.db.select(table, filters)
    
    async def get_by_id(self, table: str, id_value: str) -> Optional[Dict[str, Any]]:
        """Get a record by ID from mock database"""
        return await self.db.get_by_id(table, id_value)
    
    async def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a record into mock database"""
        return await self.db.insert(table, data)
    
    async def update(self, table: str, id_value: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a record in mock database"""
        return await self.db.update(table, id_value, data)
    
    async def delete(self, table: str, id_value: str) -> bool:
        """Delete a record from mock database"""
        return await self.db.delete(table, id_value)

# Determine whether to use Supabase or mock database
# Use environment variable to control this
USE_MOCK_DB = os.getenv("USE_MOCK_DB", "false").lower() in ("true", "1", "yes")

# If Supabase isn't available or mock DB is forced, use mock database
if not SUPABASE_AVAILABLE or USE_MOCK_DB:
    logger.info("Using mock database")
    db_client = MockClientWrapper()
else:
    logger.info("Using Supabase database")
    db_client = SupabaseClient()

async def get_db() -> DatabaseClient:
    """
    Dependency for FastAPI to get a database client.
    """
    try:
        client = await db_client.connect()
        return client
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        if not isinstance(db_client, MockClientWrapper):
            # If Supabase connection fails, fall back to mock DB
            logger.warning("Falling back to mock database")
            mock_client = MockClientWrapper()
            return await mock_client.connect()
        else:
            # If mock DB fails, something is very wrong
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database connection error: {str(e)}"
            )

async def get_admin_db() -> DatabaseClient:
    """
    Dependency for FastAPI to get an admin database client.
    """
    try:
        client = await db_client.connect_service_role()
        return client
    except Exception as e:
        logger.error(f"Admin database connection error: {str(e)}")
        if not isinstance(db_client, MockClientWrapper):
            # If Supabase connection fails, fall back to mock DB
            logger.warning("Falling back to mock database for admin operations")
            mock_client = MockClientWrapper()
            return await mock_client.connect()
        else:
            # If mock DB fails, something is very wrong
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database connection error: {str(e)}"
            )

# For testing and development (when not using dependencies)
async def get_db_client() -> DatabaseClient:
    return await db_client.connect()


async def close_db():
    """
    Close database connections.
    """
    await db_client.disconnect()


# Global database instance
db = db_client

async def init_db():
    """
    Initialize database connection and tables.
    TODO: Implement database initialization:
    - Connect to Supabase
    - Verify required tables exist
    - Set up any necessary schemas
    """
    await db.connect()

async def health_check() -> bool:
    """
    Check database connectivity.
    TODO: Implement health check:
    - Test connection to Supabase
    - Verify table access
    - Return connection status
    """
    await db.disconnect()


# TODO: Define table schemas and models
"""
Expected tables:
- users (id, email, username, created_at, updated_at)
- games (id, user_id, name, category, username, created_at)
- user_stats (id, user_id, game_id, stats_data, updated_at)
""" 