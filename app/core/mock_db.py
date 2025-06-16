"""
Mock database implementation for development and testing when Supabase is unavailable.
"""
from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime
import json
import os

class MockDatabase:
    """
    Simple in-memory database for development and testing when Supabase is unavailable.
    """
    def __init__(self):
        self.tables = {
            "profiles": {},
            "user_settings": {},
            "games": {},
            "game_stats": {},
            "activities": {},
            "game_categories": {
                # Pre-populate with some categories
                str(uuid.uuid4()): {"name": "MOBA", "description": "Multiplayer Online Battle Arena", "supported_stats": True},
                str(uuid.uuid4()): {"name": "FPS", "description": "First Person Shooter", "supported_stats": True},
                str(uuid.uuid4()): {"name": "RPG", "description": "Role Playing Game", "supported_stats": True},
            }
        }
        
        # Try to load persistent data if it exists
        self._load_data()
        
    def _load_data(self):
        """Load data from disk if it exists"""
        try:
            file_path = os.path.join(os.path.dirname(__file__), "mock_db_data.json")
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    self.tables = json.load(f)
        except Exception as e:
            print(f"Error loading mock database: {e}")
    
    def _save_data(self):
        """Save data to disk for persistence"""
        try:
            file_path = os.path.join(os.path.dirname(__file__), "mock_db_data.json")
            with open(file_path, "w") as f:
                json.dump(self.tables, f)
        except Exception as e:
            print(f"Error saving mock database: {e}")
    
    async def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a record into a table"""
        if table not in self.tables:
            self.tables[table] = {}
            
        # Generate ID if not provided
        if "id" not in data:
            data["id"] = str(uuid.uuid4())
        
        # Add timestamps
        now = datetime.now().isoformat()
        if "created_at" not in data:
            data["created_at"] = now
        if "updated_at" not in data:
            data["updated_at"] = now
            
        self.tables[table][data["id"]] = data
        self._save_data()
        return data
    
    async def select(self, table: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Select records from a table with optional filters"""
        if table not in self.tables:
            return []
            
        result = list(self.tables[table].values())
        
        if filters:
            for key, value in filters.items():
                result = [r for r in result if key in r and r[key] == value]
                
        return result
    
    async def get_by_id(self, table: str, id_value: str) -> Optional[Dict[str, Any]]:
        """Get a record by ID"""
        if table not in self.tables or id_value not in self.tables[table]:
            return None
        return self.tables[table][id_value]
    
    async def update(self, table: str, id_value: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a record by ID"""
        if table not in self.tables or id_value not in self.tables[table]:
            return None
            
        # Update timestamps
        data["updated_at"] = datetime.now().isoformat()
        
        # Update the record
        self.tables[table][id_value].update(data)
        self._save_data()
        return self.tables[table][id_value]
    
    async def delete(self, table: str, id_value: str) -> bool:
        """Delete a record by ID"""
        if table not in self.tables or id_value not in self.tables[table]:
            return False
            
        del self.tables[table][id_value]
        self._save_data()
        return True

# Singleton instance for use across the application
mock_db = MockDatabase()
