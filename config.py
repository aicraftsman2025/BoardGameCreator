# config.py
import os
import sys
import logging
from pathlib import Path

class AppConfig:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # Determine if running in bundled app
        self.is_frozen = getattr(sys, 'frozen', False)
        self.is_mac = sys.platform.startswith('darwin')
        self.is_windows = sys.platform.startswith('win')
        
        # Set up static assets path (for icons, templates, etc.)
        if self.is_frozen:
            if self.is_mac:
                bundle_dir = Path(sys.executable).parent.parent / 'Resources'
            else:
                bundle_dir = Path(sys.executable).parent
            self.ASSETS_STATIC_PATH = bundle_dir / 'assets_static'
        else:
            self.ASSETS_STATIC_PATH = Path(os.path.dirname(__file__)) / 'assets_static'

        # Set up user assets path (for user-uploaded content)
        if self.is_mac:
            self.USER_DATA_DIR = Path('~/Library/Application Support/BoardGameCreator').expanduser()
        elif self.is_windows:
            self.USER_DATA_DIR = Path(os.getenv('APPDATA')) / 'BoardGameCreator'
        else:  # Linux
            self.USER_DATA_DIR = Path('~/.boardgamecreator').expanduser()

        # User content directories
        self.ASSETS_PATH = self.USER_DATA_DIR / 'assets'  # For user-uploaded assets
        self.USER_TEMPLATES_DIR = self.USER_DATA_DIR / 'templates'
        self.USER_DB_PATH = self.USER_DATA_DIR / 'boardgame.db'
        
        # Static content directories (bundled with app)
        self.STATIC_TEMPLATES_DIR = self.ASSETS_STATIC_PATH / 'templates'
        self.STATIC_ICONS_DIR = self.ASSETS_STATIC_PATH / 'icons'
        
        # Create user directories
        self._create_user_directories()
        
        logging.info(f"App Configuration:")
        logging.info(f"ASSETS_STATIC_PATH: {self.ASSETS_STATIC_PATH}")
        logging.info(f"ASSETS_PATH: {self.ASSETS_PATH}")
        logging.info(f"USER_DATA_DIR: {self.USER_DATA_DIR}")
        logging.info(f"USER_DB_PATH: {self.USER_DB_PATH}")
        
        self._initialized = True

    def _create_user_directories(self):
        """Create necessary user directories"""
        directories = [
            self.USER_DATA_DIR,
            self.ASSETS_PATH,
            self.USER_TEMPLATES_DIR
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logging.info(f"Created directory: {directory}")
            except Exception as e:
                logging.error(f"Error creating directory {directory}: {str(e)}")
                raise

    def get_static_icon_path(self, icon_name):
        """Get path to a static icon file"""
        return self.STATIC_ICONS_DIR / icon_name

    def get_static_template_path(self, template_name):
        """Get path to a static template file"""
        return self.STATIC_TEMPLATES_DIR / template_name

    def get_asset_path(self, asset_name):
        """Get path to a user asset file"""
        return self.ASSETS_PATH / asset_name

    def get_template_path(self, template_name):
        """Get path to a user template file"""
        return self.USER_TEMPLATES_DIR / template_name

# Create a global instance
config = AppConfig()

# Add a function to get the config instance
def get_config():
    return config