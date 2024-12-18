import customtkinter as ctk
from PIL import Image
import os
import importlib.util
import sys
from config import get_config
import logging
from utils.path_utils import get_resource_path

class ScriptApp:
    def __init__(self, title, description, script_path, icon_path=None):
        self.title = title
        self.description = description
        self.script_path = script_path
        self.config = get_config()
        # Use ASSETS_STATIC_PATH for default icon path
        self.icon_path = icon_path or os.path.join(self.config.ASSETS_STATIC_PATH, "icons", "script.png")
        self.module = None
        
    def load_module(self):
        """Dynamically load the script module"""
        try:
            spec = importlib.util.spec_from_file_location(
                os.path.basename(self.script_path),
                self.script_path
            )
            self.module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = self.module
            spec.loader.exec_module(self.module)
            return True
        except Exception as e:
            logging.error(f"Error loading module {self.script_path}: {e}")
            return False

class GenerativeTools(ctk.CTkFrame):
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.config = get_config()
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_header()
        self._create_tools_grid()
        
        # Register available script apps
        self._register_script_apps()
        
        # Populate the grid with script apps
        self._populate_tools_grid()
    
    def _create_header(self):
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        
        title = ctk.CTkLabel(
            header,
            text="Generative Tools",
            font=("Helvetica", 24, "bold")
        )
        title.pack(pady=10)
    
    def _create_tools_grid(self):
        # Create scrollable frame for tools
        self.tools_frame = ctk.CTkScrollableFrame(self)
        self.tools_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.tools_frame.grid_columnconfigure(0, weight=1)
    
    def _register_script_apps(self):
        """Register available script applications"""
        self.script_apps = [
            ScriptApp(
                title="Generate Map",
                description="Generate a random board game map with different node types and connections.",
                script_path=get_resource_path(os.path.join('utils', 'scripts', 'generate_map.py')),
                icon_path=os.path.join(self.config.ASSETS_STATIC_PATH, "icons", "map.png")
            ),
            ScriptApp(
                title="Generate Crossword",
                description="Create crossword puzzles from word lists in CSV files.",
                script_path=get_resource_path(os.path.join('utils', 'scripts', 'generate_map.py'))  ,
                icon_path=os.path.join(self.config.ASSETS_STATIC_PATH, "icons", "crossword.png")
            ),
            ScriptApp(
                title="Generate AI Assets",
                description="Generate pixel art assets using AI from CSV prompts.",
                script_path=get_resource_path(os.path.join('utils', 'scripts', 'generate_asset_ai.py')),
                icon_path=os.path.join(self.config.ASSETS_STATIC_PATH, "icons", "ai_asset.png")
            ),
        ]
    
    def _populate_tools_grid(self):
        """Populate the grid with script app cards"""
        for i, app in enumerate(self.script_apps):
            self._create_script_card(app, i)
    
    def _create_script_card(self, app, index):
        """Create a card for a script app"""
        # Card frame
        card = ctk.CTkFrame(self.tools_frame)
        card.grid(row=index, column=0, sticky="ew", padx=10, pady=5)
        card.grid_columnconfigure(1, weight=1)
        
        # Icon
        try:
            if os.path.exists(app.icon_path):
                icon_image = ctk.CTkImage(
                    light_image=Image.open(app.icon_path),
                    dark_image=Image.open(app.icon_path),
                    size=(32, 32)
                )
                icon = ctk.CTkLabel(card, image=icon_image, text="")
                icon.grid(row=0, column=0, rowspan=2, padx=10, pady=10)
            else:
                logging.warning(f"Icon not found at: {app.icon_path}")
                icon = ctk.CTkLabel(card, text="📜")
                icon.grid(row=0, column=0, rowspan=2, padx=10, pady=10)
        except Exception as e:
            logging.error(f"Error loading icon for {app.title}: {e}")
            # Fallback if icon loading fails
            icon = ctk.CTkLabel(card, text="📜")
            icon.grid(row=0, column=0, rowspan=2, padx=10, pady=10)
        
        # Title
        title = ctk.CTkLabel(
            card,
            text=app.title,
            font=("Helvetica", 16, "bold"),
            anchor="w"
        )
        title.grid(row=0, column=1, sticky="w", padx=5, pady=(10, 0))
        
        # Description
        description = ctk.CTkLabel(
            card,
            text=app.description,
            anchor="w",
            wraplength=400
        )
        description.grid(row=1, column=1, sticky="w", padx=5, pady=(0, 10))
        
        # Run button
        run_btn = ctk.CTkButton(
            card,
            text="Run",
            width=100,
            command=lambda a=app: self._run_script(a)
        )
        run_btn.grid(row=0, column=2, rowspan=2, padx=10, pady=10)
    
    def _run_script(self, app):
        """Execute the selected script"""
        try:
            if app.load_module():
                # Get script instance
                script_instance = app.module.main()
                
                # Set asset controller if available
                if hasattr(self.controller, 'asset_controller'):
                    script_instance.asset_controller = self.controller.asset_controller
                
                # Create and show the configuration dialog
                script_instance.create_dialog(self)
                
        except Exception as e:
            print(f"Error running script: {e}") 