import json
from typing import Dict, Optional
import sqlite3

class SettingsController:
    def __init__(self, db):
        # If db is a DatabaseManager instance, get its connection
        if hasattr(db, 'connection'):
            self.db = db.connection
        # If db is a path, create a connection
        elif isinstance(db, str):
            self.db = sqlite3.connect(db)
            self.db.row_factory = sqlite3.Row
            self.initialize_database()
        # If db is already a connection, use it
        else:
            self.db = db
    
    def get_settings(self) -> Optional[Dict]:
        """Get current application settings"""
        query = "SELECT settings FROM app_settings WHERE id = 1"
        cursor = self.db.cursor()
        result = cursor.execute(query).fetchone()
        
        if result:
            return json.loads(result['settings'])
        return self._get_default_settings()
    
    def save_settings(self, settings: Dict) -> bool:
        """Save application settings"""
        query = """
            INSERT OR REPLACE INTO app_settings (id, settings)
            VALUES (1, ?)
        """
        cursor = self.db.cursor()
        cursor.execute(query, (json.dumps(settings),))
        self.db.commit()
        return True
    
    def update_setting(self, path: str, value: any) -> bool:
        """Update a specific setting by path (e.g., 'theme.mode')"""
        settings = self.get_settings() or self._get_default_settings()
        
        # Navigate to the correct setting
        current = settings
        path_parts = path.split('.')
        
        # Navigate to the parent of the setting to update
        for part in path_parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Update the setting
        current[path_parts[-1]] = value
        
        return self.save_settings(settings)
    
    def _get_default_settings(self) -> Dict:
        """Get default settings"""
        return {
            'api_keys': {
                'openai': '',
                'claude': ''
            },
            'paths': {
                'assets': 'assets'
            }
        }
    
    def initialize_database(self):
        """Initialize the settings table"""
        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_settings (
                id INTEGER PRIMARY KEY,
                settings TEXT NOT NULL
            )
        ''')
        
        # Insert default settings if not exists
        cursor.execute("SELECT COUNT(*) FROM app_settings WHERE id = 1")
        if cursor.fetchone()[0] == 0:
            self.save_settings(self._get_default_settings())
        
        self.db.commit()