import json
from typing import Dict, Optional
from models.db_manager import DatabaseManager

class SettingsController:
    def __init__(self, db):
        self.db = db
    
    def get_settings(self) -> Optional[Dict]:
        """Get current application settings"""
        query = "SELECT settings FROM app_settings WHERE id = 1"
        result = self.db.execute(query).fetchone()
        
        if result:
            return json.loads(result['settings'])
        return None
    
    def save_settings(self, settings: Dict) -> bool:
        """Save application settings"""
        query = """
            INSERT OR REPLACE INTO app_settings (id, settings)
            VALUES (1, ?)
        """
        self.db.execute(query, (json.dumps(settings),))
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