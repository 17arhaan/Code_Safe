"""Database connection and operations."""
import sqlite3
from typing import List, Dict, Any

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        """Connect to database."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
    
    def execute(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute query and return results."""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
