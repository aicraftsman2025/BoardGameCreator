import os
import json
import shutil
from datetime import datetime
from models.asset import Asset
from PIL import Image
from typing import Optional
import sqlite3
from controllers.settings_controller import SettingsController

class AssetController:
    def __init__(self, db):
        # If db is a DatabaseManager instance, get its path
        if hasattr(db, 'db_path'):
            db_path = db.db_path
        elif isinstance(db, str):
            db_path = db
        else:
            db_path = db
        
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self.initialize_database()
        
        # Get asset directory from settings or use default
        settings_controller = SettingsController(db_path)
        settings = settings_controller.get_settings()
        self.asset_dir = settings.get('paths', {}).get('assets', "assets")
        os.makedirs(self.asset_dir, exist_ok=True)
    
    def import_asset(self, file_path: str, folder_name: Optional[str] = None) -> Asset:
        # Generate unique filename
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        
        # Determine target directory
        target_dir = self.asset_dir
        if folder_name:
            target_dir = os.path.join(self.asset_dir, folder_name)
            os.makedirs(target_dir, exist_ok=True)
        
        new_path = os.path.join(target_dir, filename)
        
        # Ensure unique filename
        counter = 1
        while os.path.exists(new_path):
            new_path = os.path.join(target_dir, f"{name}_{counter}{ext}")
            counter += 1
        
        # Copy file to assets directory
        shutil.copy2(file_path, new_path)
        
        # Get file metadata
        metadata = self._get_file_metadata(new_path)
        
        # Save to database
        query = """
            INSERT INTO assets 
            (name, folder, file_path, file_type, metadata)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor = self.connection.execute(
            query,
            (
                name,
                folder_name,
                new_path,
                ext.lower()[1:],
                json.dumps(metadata)
            )
        )
        self.connection.commit()
        
        return self.get_asset_by_id(cursor.lastrowid)
    
    def get_asset_by_id(self, asset_id: int) -> Asset:
        query = "SELECT * FROM assets WHERE asset_id = ?"
        cursor = self.connection.execute(query, (asset_id,))
        row = cursor.fetchone()
        return Asset.from_db_row(row) if row else None
    
    def get_all_assets(self, folder_name: Optional[str] = None) -> list:
        """
        Get all assets, optionally filtered by folder
        
        Args:
            folder_name: Optional folder name to filter assets
        
        Returns:
            list: List of Asset objects
        """
        if folder_name:
            folder_path = os.path.join(self.asset_dir, folder_name)
            query = "SELECT * FROM assets WHERE file_path LIKE ? ORDER BY created_at DESC"
            cursor = self.connection.cursor()
            cursor = cursor.execute(query, (f"{folder_path}%",))
        else:
            query = "SELECT * FROM assets ORDER BY created_at DESC"
            cursor = self.connection.cursor()
            cursor = cursor.execute(query)
        
        return [Asset.from_db_row(row) for row in cursor.fetchall()]
    
    def delete_asset(self, asset_id: int) -> bool:
        # Get asset info
        asset = self.get_asset_by_id(asset_id)
        if not asset:
            return False
        
        # Delete file
        if os.path.exists(asset.file_path):
            os.remove(asset.file_path)
        
        # Delete from database
        query = "DELETE FROM assets WHERE asset_id = ?"
        self.connection.execute(query, (asset_id,))
        self.connection.commit()
        
        return True
    
    def _get_file_metadata(self, file_path: str) -> dict:
        metadata = {
            'size': os.path.getsize(file_path),
            'created': datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
        }
        
        # Get image-specific metadata
        try:
            with Image.open(file_path) as img:
                metadata.update({
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode
                })
        except:
            pass
        
        return metadata
    
    def get_asset_folders(self):
        """
        Retrieve all asset folders from the filesystem
        Returns a list of folder names
        """
        try:
            folders = [f for f in os.listdir(self.asset_dir) if os.path.isdir(os.path.join(self.asset_dir, f))]
            return folders
        except Exception as e:
            print(f"Error loading asset folders: {e}")
            return []
    
    def get_assets(self) -> list:
        return self.get_all_assets()
    
    def get_folder_path(self, folder_name: str) -> Optional[str]:
        """
        Get the filesystem path for a folder by its name.
        
        Args:
            folder_name: Name of the folder
        
        Returns:
            str: Path to the folder or None if not found
        """
        folder_path = os.path.join(self.asset_dir, folder_name)
        return folder_path if os.path.isdir(folder_path) else None
    
    def get_assets_count(self, folder_name: Optional[str] = None) -> int:
        """
        Get total count of assets, optionally filtered by folder
        
        Args:
            folder_name: Optional folder name to filter assets
        
        Returns:
            int: Total number of assets
        """
        if folder_name:
            folder_path = os.path.join(self.asset_dir, folder_name)
            query = "SELECT COUNT(*) as count FROM assets WHERE file_path LIKE ?"
            cursor = self.connection.execute(query, (f"{folder_path}%",))
        else:
            query = "SELECT COUNT(*) as count FROM assets"
            cursor = self.connection.execute(query)
        
        result = cursor.fetchone()
        return result['count'] if result else 0
    
    def create_asset_folder(self, folder_name: str, parent_id: Optional[int] = None) -> str:
        """
        Create a new asset folder in the filesystem.
        
        Args:
            folder_name: Name of the new folder
            parent_id: Not used anymore, kept for backward compatibility
        
        Returns:
            str: Path to the created folder
        """
        folder_path = os.path.join(self.asset_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path
    
    def delete_folder(self, folder_name: str) -> bool:
        """
        Delete a folder and all its contents.
        
        Args:
            folder_name: Name of the folder to delete
        
        Returns:
            bool: True if successful, False otherwise
        """
        folder_path = os.path.join(self.asset_dir, folder_name)
        try:
            if os.path.exists(folder_path):
                # Delete all assets in the folder from database
                query = "DELETE FROM assets WHERE file_path LIKE ?"
                self.connection.execute(query, (f"{folder_path}%",))
                self.connection.commit()
                
                # Delete the physical folder
                shutil.rmtree(folder_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting folder {folder_name}: {e}")
            return False
    
    def initialize_database(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assets (
                asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                folder TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.connection.commit()
    
    def update_asset_path(self, new_path: str):
        """Update the asset directory path and move existing assets"""
        if new_path == self.asset_dir:
            return
        
        # Create new directory
        os.makedirs(new_path, exist_ok=True)
        
        # Move existing assets if any exist
        if os.path.exists(self.asset_dir):
            for item in os.listdir(self.asset_dir):
                src = os.path.join(self.asset_dir, item)
                dst = os.path.join(new_path, item)
                shutil.move(src, dst)
                
                # Update database paths
                if os.path.isfile(src):
                    query = """
                        UPDATE assets 
                        SET file_path = REPLACE(file_path, ?, ?)
                        WHERE file_path LIKE ?
                    """
                    self.connection.execute(query, (self.asset_dir, new_path, f"{self.asset_dir}%"))
        
        self.asset_dir = new_path
        self.connection.commit()
    
    def get_assets_page(self, offset: int = 0, limit: int = 12, folder_name: Optional[str] = None) -> list:
        """
        Get paginated assets, optionally filtered by folder
        
        Args:
            offset: Number of records to skip
            limit: Maximum number of records to return
            folder_name: Optional folder name to filter assets
        
        Returns:
            list: List of Asset objects for the current page
        """
        if folder_name:
            folder_path = os.path.join(self.asset_dir, folder_name)
            query = """
                SELECT * FROM assets 
                WHERE file_path LIKE ? 
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            cursor = self.connection.execute(query, (f"{folder_path}%", limit, offset))
        else:
            query = """
                SELECT * FROM assets 
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            cursor = self.connection.execute(query, (limit, offset))
        
        return [Asset.from_db_row(row) for row in cursor.fetchall()]