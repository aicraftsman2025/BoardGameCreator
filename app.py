import customtkinter as ctk
from views.project_view import ProjectSelectionView, selected_project, project_id
from views.main_view import MainView
from models.db_manager import DatabaseManager
from controllers.project_controller import ProjectController
from controllers.component_controller import ComponentController
from controllers.template_controller import TemplateController
from controllers.asset_controller import AssetController
from controllers.settings_controller import SettingsController
from controllers.csv_controller import CSVController
import os
from PIL import Image, ImageTk
import sys
import traceback
import logging
from datetime import datetime
from config import get_config

# Immediate console output for debugging
print("Starting application...")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Executable path: {sys.executable}")

# Try multiple logging locations
LOG_LOCATIONS = [
    os.path.expanduser('~/Library/Logs/BoardGameCreator/debug.log'),
    'boardgame_creator.log'  # Current directory
]

def setup_logging():
    for log_path in LOG_LOCATIONS:
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
                handlers=[
                    logging.FileHandler(log_path, encoding='utf-8', mode='w'),
                    logging.StreamHandler(sys.stdout)
                ]
            )
            print(f"Logging to: {log_path}")
            return True
        except Exception as e:
            print(f"Failed to set up logging at {log_path}: {e}")
    return False

# Try to set up logging
if not setup_logging():
    print("Failed to set up logging at all locations!")
    sys.exit(1)

logger = logging.getLogger(__name__)
logger.info("Logger initialized")

def exception_handler(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions"""
    logger.error("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))
    
# Set the global exception handler
sys.excepthook = exception_handler

class App(ctk.CTk):
    def __init__(self):
        try:
            logger.info("Initializing App...")
            
            # Set theme before initializing
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")
            
            super().__init__()
            self.config = get_config()
            logger.info("Config loaded successfully")
            
            self.title("Board Game Creator")
            self.geometry("1024x768")
            
            # Load icon
            try:
                icon_path = self.config.get_static_icon_path("app_icon.ico")
                logger.info(f"Loading icon from: {icon_path}")
                
                if icon_path.exists():
                    if self.config.is_mac:
                        icon = Image.open(icon_path)
                        photo = ImageTk.PhotoImage(icon)
                        self.iconphoto(True, photo)
                    else:
                        self.iconbitmap(icon_path)
                else:
                    logger.warning(f"Icon not found at: {icon_path}")
            except Exception as e:
                logger.error(f"Error loading icon: {e}")
            
            # Initialize database
            try:
                logger.info(f"Initializing database with path: {self.config.USER_DB_PATH}")
                self.db = DatabaseManager(str(self.config.USER_DB_PATH))
                logger.info("Database initialized successfully")
            except Exception as e:
                logger.error(f"Database initialization failed: {e}")
                raise
            
            # Initialize controllers
            try:
                logger.info("Initializing controllers...")
                self.controllers = {
                    'project': ProjectController(self.db),
                    'component': ComponentController(self.db),
                    'template': TemplateController(self.db),
                    'asset': AssetController(self.db),
                    'settings': SettingsController(self.db),
                    'csv': CSVController()
                }
                logger.info("Controllers initialized successfully")
            except Exception as e:
                logger.error(f"Controller initialization failed: {e}")
                raise
            
            # Initialize project view
            try:
                logger.info("Creating project selection view...")
                self.project_view = ProjectSelectionView(
                    parent=self,
                    on_project_selected=self.on_project_selected,
                    controller=self.controllers['project']
                )
                self.project_view.pack(fill="both", expand=True)
                logger.info("Project view created successfully")
            except Exception as e:
                logger.error(f"Project view creation failed: {e}")
                raise
            
            self.main_view = None
            logger.info("App initialization completed successfully")
            
        except Exception as e:
            logger.critical(f"Critical error in App initialization: {e}")
            logger.critical(traceback.format_exc())
            raise
    
    def on_project_selected(self, project_name):
        try:
            logger.info(f"Project selected: {project_name}")
            self.project_view.pack_forget()
            self.main_view = MainView(self, self.controllers)
            self.main_view.pack(fill="both", expand=True)
            logger.info("Main view loaded successfully")
        except Exception as e:
            logger.error(f"Error switching to main view: {e}")
            raise

def check_permissions():
    print("\nPermissions Check:")
    paths_to_check = [
        os.path.expanduser('~/Desktop'),
        os.path.expanduser('~/Library/Application Support'),
        os.getcwd()
    ]
    
    for path in paths_to_check:
        try:
            print(f"\nChecking {path}:")
            print(f"Exists: {os.path.exists(path)}")
            print(f"Readable: {os.access(path, os.R_OK)}")
            print(f"Writable: {os.access(path, os.W_OK)}")
            print(f"Executable: {os.access(path, os.X_OK)}")
        except Exception as e:
            print(f"Error checking {path}: {e}")

def main():
    try:
        logger.info("="*50)
        logger.info(f"Application starting at {datetime.now()}")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Platform: {sys.platform}")
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Executable path: {sys.executable}")
        
        config = get_config()
        logger.info("Configuration loaded")
        
        app = App()
        logger.info("Starting main loop")
        app.mainloop()
        logger.info("Application closed normally")
        
    except Exception as e:
        logger.critical(f"Critical error during startup: {e}")
        logger.critical(traceback.format_exc())
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main() 