import customtkinter as ctk
from views.project_view import ProjectSelectionView, selected_project, project_id
from views.main_view import MainView
from models.db_manager import DatabaseManager  # This import looks correct based on the code context
from controllers.project_controller import ProjectController
from controllers.component_controller import ComponentController
from controllers.template_controller import TemplateController
from controllers.asset_controller import AssetController
from controllers.settings_controller import SettingsController
from controllers.csv_controller import CSVController

class App(ctk.CTk):
    def __init__(self):
        # Set theme before initializing - enforce dark mode
        ctk.set_appearance_mode("dark")  # Set dark mode and never change it
        ctk.set_default_color_theme("blue")
        
        super().__init__()
        self.title("Board Game Designer")
        self.geometry("1024x768")
        
        # Configure dark theme colors
        self.configure(fg_color="#1a1a1a")  # Very dark gray background
        
        # Set default colors for CustomTkinter widgets
        ctk.set_widget_scaling(1.0)  # Ensure consistent widget sizing
        
        # Configure grid weights for responsive layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Initialize database and controllers
        self.db = DatabaseManager()  # Add your database initialization
        
        # Create controllers dictionary
        self.controllers = {
            'project': ProjectController(self.db),
            'component': ComponentController(self.db),
            'template': TemplateController(self.db),
            'asset': AssetController(self.db),
            'settings': SettingsController(self.db),
            'csv': CSVController()
        }
        
        # Start with project selection
        self.project_view = ProjectSelectionView(
            parent=self,
            on_project_selected=self.on_project_selected,
            controller=self.controllers['project']
        )
        self.project_view.pack(fill="both", expand=True)
        
        self.main_view = None
        
    def on_project_selected(self, project_name):
        # Create a dictionary of controllers
        controllers = {
            'project': None,  # Add your actual controller instances here
            'component': None,
            'template': None,
            'asset': None,
            'settings': None,
            'csv': None
        }
        
        self.project_view.pack_forget()
        self.main_view = MainView(self, self.controllers)
        self.main_view.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop() 