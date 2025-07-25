import logging
from .simple_db import SimpleDB

logger = logging.getLogger(__name__)

# Singleton pattern - one database instance for the whole application
class DatabaseManager:
    _instance = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._db = SimpleDB()
            logger.info("Shared database instance created")
        return cls._instance
    
    def get_db(self):
        return self._db

# Global instance
db_manager = DatabaseManager()

def get_shared_db():
    """Get the shared database instance"""
    return db_manager.get_db()