import customtkinter as ctk
from views.project_view import ProjectSelectionView
from views.component_editor import ComponentEditor
from views.asset_manager import AssetManager
from views.settings_view import SettingsView
from views.template_manager import TemplateManager

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
        # Sidebar frame with dark theme
        self.sidebar = ctk.CTkFrame(self, fg_color="#2b2b2b")  # Slightly lighter than background
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.sidebar.grid_rowconfigure(5, weight=1)  # Push settings to bottom
        
        # App Title
        title_label = ctk.CTkLabel(
            self.sidebar,
            text="Board Game Designer",
            font=("Helvetica", 16, "bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Navigation Buttons
        self.nav_buttons = {}
        
        # Projects Button with project name
        button_text = f"Projects - {self.current_project}" if self.current_project else "Projects"
        self.nav_buttons["project"] = ctk.CTkButton(
            self.sidebar,
            text=button_text,
            command=lambda: self.show_view("project")
        )
        self.nav_buttons["project"].grid(row=1, column=0, padx=20, pady=5)
        
        # Component Editor Button
        self.nav_buttons["component"] = ctk.CTkButton(
            self.sidebar,
            text="Component Editor",
            command=lambda: self.show_view("component")
        )
        self.nav_buttons["component"].grid(row=2, column=0, padx=20, pady=5)
        
        # Asset Manager Button
        self.nav_buttons["asset"] = ctk.CTkButton(
            self.sidebar,
            text="Asset Manager",
            command=lambda: self.show_view("asset")
        )
        self.nav_buttons["asset"].grid(row=3, column=0, padx=20, pady=5)
         # Template Manager Button
        self.nav_buttons["template"] = ctk.CTkButton(
            self.sidebar,
            text="Template Manager",
            command=lambda: self.show_view("template")
        )
        self.nav_buttons["template"].grid(row=4, column=0, padx=20, pady=5)
        # Settings Button (at bottom)
        self.nav_buttons["settings"] = ctk.CTkButton(
            self.sidebar,
            text="Settings",
            command=lambda: self.show_view("settings")
        )
        self.nav_buttons["settings"].grid(row=5, column=0, padx=20, pady=20, sticky="s")
        
        
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
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
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