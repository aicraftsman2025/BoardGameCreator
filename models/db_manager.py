import sqlite3
import os
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with schema if it doesn't exist"""
        is_new_db = not os.path.exists(self.db_path)
        
        # Create connection (will create db file if it doesn't exist)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        if is_new_db:
            print("New database detected. Initializing schema...")
            self._init_schema()
        
    def _init_schema(self):
        """Initialize database schema from schema.sql"""
        try:
            # Read schema file
            schema_path = os.path.join(os.path.dirname(__file__), '.', 'schema.sql')
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            # Execute schema
            cursor = self.conn.cursor()
            cursor.executescript(schema_sql)
            self.conn.commit()
            print("Schema initialized successfully")
        except Exception as e:
            print(f"Error initializing schema: {e}")
            raise
    
    def execute(self, query, params=()):
        """Execute a query and return the cursor"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor
    
    def commit(self):
        """Commit the current transaction"""
        self.conn.commit()
    
    def close(self):
        """Close the database connection"""
        self.conn.close()
    

    def get_all_projects(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM projects ORDER BY updated_at DESC')
        return cursor.fetchall()
    
    def create_project(self, name, description=""):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO projects (name, description)
            VALUES (?, ?)
        ''', (name, description))
        return cursor.lastrowid

    def add_card(self, project_id, name, description="", image_path="", attributes=None):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO cards (project_id, name, description, image_path, attributes)
            VALUES (?, ?, ?, ?, ?)
        ''', (project_id, name, description, image_path, json.dumps(attributes or {})))
        return cursor.lastrowid

    def update_game_settings(self, project_id, board_layout=None, rules="", player_count=2):
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO game_settings 
            (project_id, board_layout, rules, player_count)
            VALUES (?, ?, ?, ?)
        ''', (project_id, json.dumps(board_layout or {}), rules, player_count))
        return cursor.lastrowid

    def initialize_default_templates(self):
        DEFAULT_TEMPLATES = [
            {
                'name': 'Standard Playing Card',
                'type': 'Cards',
                'category': 'playing_cards',
                'properties': {
                    'dimensions': {'width': 63, 'height': 88},
                    'corners': 'rounded',
                    'layout': {
                        'areas': [
                            {'name': 'top_value', 'x': 5, 'y': 5, 'width': 15, 'height': 15},
                            {'name': 'center_art', 'x': 10, 'y': 20, 'width': 43, 'height': 48},
                            {'name': 'bottom_value', 'x': 43, 'y': 68, 'width': 15, 'height': 15}
                        ]
                    }
                }
            },
            {
                'name': 'Hexagonal Tile',
                'type': 'Tokens',
                'category': 'board_tiles',
                'properties': {
                    'dimensions': {'width': 50, 'height': 57.74},
                    'shape': 'hexagon',
                    'layout': {
                        'areas': [
                            {'name': 'main_content', 'x': 5, 'y': 5, 'width': 40, 'height': 47.74}
                        ]
                    }
                }
            }
        ]
        
        cursor = self.conn.cursor()
        for template in DEFAULT_TEMPLATES:
            cursor.execute("""
                INSERT OR IGNORE INTO card_templates 
                (name, structure)
                VALUES (?, ?)
            """, (
                template['name'],
                json.dumps(template)
            ))
        self.connection.commit()