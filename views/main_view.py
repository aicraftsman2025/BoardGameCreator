import customtkinter as ctk
from views.project_view import ProjectSelectionView
from views.component_editor import ComponentEditor
from views.asset_manager import AssetManager
from views.settings_view import SettingsView
from views.template_manager import TemplateManager
from views.components_manager import ComponentsManager
from views.csv_manager import CSVManager
from views.card_factory import CardFactory
from views.pdf_exporter import PDFExporter
from views.generative_tools import GenerativeTools
from PIL import Image

class MainView(ctk.CTkFrame):
    def __init__(self, parent, controllers):
        super().__init__(parent)
        self.configure(fg_color="#1a1a1a")  # Match app's dark background
        
        self.controllers = controllers
        self.current_view = None
        
        # Get the selected project name from the global variable
        from views.project_view import selected_project
        self.current_project = selected_project
        
        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._create_sidebar()
        self._create_content_area()
        
        # Show appropriate view
        if self.current_project:
            self.show_view("component")
        else:
            self.show_view("project")
    
    def _create_sidebar(self):
        # Import icons
        self.icons = {
            "project": ctk.CTkImage(
                light_image=Image.open("assets_static/icons/project.png"),
                dark_image=Image.open("assets_static/icons/project.png"),
                size=(20, 20)
            ),
            "component": ctk.CTkImage(
                light_image=Image.open("assets_static/icons/component.png"),
                dark_image=Image.open("assets_static/icons/component.png"),
                size=(20, 20)
            ),
            "components": ctk.CTkImage(
                light_image=Image.open("assets_static/icons/component.png"),
                dark_image=Image.open("assets_static/icons/component.png"),
                size=(20, 20)
            ),
            "template": ctk.CTkImage(
                light_image=Image.open("assets_static/icons/template.png"),
                dark_image=Image.open("assets_static/icons/template.png"),
                size=(20, 20)
            ),
            "factory": ctk.CTkImage(
                light_image=Image.open("assets_static/icons/factory.png"),
                dark_image=Image.open("assets_static/icons/factory.png"),
                size=(20, 20)
            ),
            "csv": ctk.CTkImage(
                light_image=Image.open("assets_static/icons/csv.png"),
                dark_image=Image.open("assets_static/icons/csv.png"),
                size=(20, 20)
            ),
            "pdf": ctk.CTkImage(
                light_image=Image.open("assets_static/icons/pdf.png"),
                dark_image=Image.open("assets_static/icons/pdf.png"),
                size=(20, 20)
            ),
            "asset": ctk.CTkImage(
                light_image=Image.open("assets_static/icons/asset.png"),
                dark_image=Image.open("assets_static/icons/asset.png"),
                size=(20, 20)
            ),
            "settings": ctk.CTkImage(
                light_image=Image.open("assets_static/icons/setting.png"),
                dark_image=Image.open("assets_static/icons/setting.png"),
                size=(20, 20)
            ),
            "generative": ctk.CTkImage(
                light_image=Image.open("assets_static/icons/generative.png"),
                dark_image=Image.open("assets_static/icons/generative.png"),
                size=(20, 20)
            )
        }

        # Sidebar frame with dark theme
        self.sidebar = ctk.CTkFrame(self, fg_color="#2b2b2b", width=200)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.sidebar.grid_rowconfigure(9, weight=1)  # Push settings to bottom
        self.sidebar.grid_propagate(False)  # Prevent sidebar from shrinking
        
        # App Title
        title_label = ctk.CTkLabel(
            self.sidebar,
            text="Board Game Creator",
            font=("Helvetica", 16, "bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 30))
        
        # Navigation Buttons
        self.nav_buttons = {}
        
        # Define button configurations
        button_configs = [
            {
                "key": "project",
                "text": f"Project: {self.current_project or 'Select Project'}",
                "row": 1,
                "icon": "project"
            },
            {
                "key": "component",
                "text": "Design Component",
                "row": 2,
                "icon": "component"
            },
            {
                "key": "components",
                "text": "Manage Components",
                "row": 3,
                "icon": "components"
            },
            {
                "key": "template",
                "text": "Card Templates",
                "row": 4,
                "icon": "template"
            },
            {
                "key": "factory",
                "text": "Export Cards",
                "row": 5,
                "icon": "factory"
            },
            {
                "key": "csv",
                "text": "Import Data",
                "row": 6,
                "icon": "csv"
            },
            {
                "key": "pdf",
                "text": "Export to PDF",
                "row": 7,
                "icon": "pdf"
            },
            {
                "key": "asset",
                "text": "Asset Library",
                "row": 8,
                "icon": "asset"
            },
            {
                "key": "settings",
                "text": "Settings",
                "row": 10,
                "icon": "settings",
                "sticky": "sew"
            },
            {
                "key": "generative",
                "text": "Generative Tools",
                "row": 9,
                "icon": "generative"
            }
        ]
        
        # Create buttons with consistent styling
        for config in button_configs:
            self.nav_buttons[config["key"]] = ctk.CTkButton(
                self.sidebar,
                text=config["text"],
                image=self.icons[config["icon"]],
                command=lambda k=config["key"]: self.show_view(k),
                anchor="w",  # Align text to the left
                height=40,
                corner_radius=8,
                fg_color="transparent",  # Make button transparent by default
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray35"),
                compound="left",  # Place icon to the left of the text
                width=180
            )
            sticky = config.get("sticky", "ew")  # Default to east-west fill
            self.nav_buttons[config["key"]].grid(
                row=config["row"],
                column=0,
                padx=10,
                pady=5,
                sticky=sticky
            )
    
    def _create_content_area(self):
        # Content frame with dark theme
        self.content_frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
    
    def show_view(self, view_name):
        # Update button colors
        for name, button in self.nav_buttons.items():
            if name == view_name:
                button.configure(fg_color=("gray75", "gray25"))
            else:
                button.configure(fg_color=("gray70", "gray30"))
        
        # Clear current content
        if self.current_view:
            self.current_view.destroy()  # Properly destroy the current view
        
        # Show requested view
        if view_name == "project":
            self.current_view = ProjectSelectionView(
                parent=self.content_frame,
                on_project_selected=self.on_project_selected,
                controller=self.controllers['project']
            )
        elif view_name == "component":
            self.current_view = ComponentEditor(
                self.content_frame,
                self.controllers['component'],
                self.controllers['template'],
                self.controllers['asset']
            )
        elif view_name == "asset":
            self.current_view = AssetManager(
                self.content_frame,
                self.controllers['asset']
            )
        elif view_name == "settings":
            self.current_view = SettingsView(
                self.content_frame,
                self.controllers['settings']
            )
        elif view_name == "template":
            self.current_view = TemplateManager(
                self.content_frame,
                self.controllers['template']
            )
        elif view_name == "components":
            self.current_view = ComponentsManager(
                self.content_frame,
                self.controllers['component'],
                self.controllers['template']
            )
        elif view_name == "csv":
            self.current_view = CSVManager(
                self.content_frame,
                self.controllers['csv']
            )
        elif view_name == "factory":
            self.current_view = CardFactory(
                self.content_frame,
                self.controllers['template'],
                self.controllers['csv']
            )
        elif view_name == "pdf":  # Add PDF Exporter view
            self.current_view = PDFExporter(
                self.content_frame,
                self.controllers['template'],
                self.controllers['csv']
            )
        elif view_name == "generative":
            self.current_view = GenerativeTools(
                self.content_frame,
                self.controllers.get('generative')
            )
        
        if self.current_view:
            self.current_view.pack(fill="both", expand=True)
    
    def on_project_selected(self, project_name):
        """Handle project selection and switch to component editor"""
        self.update_project_button(project_name)
        self.current_project = project_name
        # Ensure we switch to component editor after project selection
        self.show_view("component")
    
    def update_project_button(self, project_name):
        """Update the projects button text with the selected project name"""
        self.current_project = project_name
        self.nav_buttons["project"].configure(text=f"Projects - {project_name}")