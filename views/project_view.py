import customtkinter as ctk
from typing import List, Optional

# Global variables to store selection
selected_project = None
project_id = None

class ProjectSelectionView(ctk.CTkFrame):
    def __init__(self, parent, on_project_selected, controller):
        super().__init__(parent)
        self.on_project_selected = on_project_selected
        self.controller = controller
        
        # Create main container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(expand=True, pady=50)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.main_container,
            text="Board Game Designer",
            font=("Helvetica", 24, "bold")
        )
        self.title_label.pack(pady=(0, 30))
        
        # Project selection container
        self.selection_container = ctk.CTkFrame(self.main_container)
        self.selection_container.pack(fill="x", padx=20, pady=10)
        
        # Project Dropdown
        self.project_var = ctk.StringVar()
        self.project_dropdown = ctk.CTkOptionMenu(
            self.selection_container,
            variable=self.project_var,
            values=["No projects available"],
            state="disabled",
            width=200
        )
        self.project_dropdown.pack(pady=10)
        
        # Buttons container
        self.button_container = ctk.CTkFrame(self.main_container)
        self.button_container.pack(fill="x", padx=20, pady=10)
        
        # Create Project Button
        self.create_button = ctk.CTkButton(
            self.button_container,
            text="Create New Project",
            command=self.show_create_project_dialog
        )
        self.create_button.pack(pady=5)
        
        # Action buttons frame (for Open and Delete)
        self.action_buttons_frame = ctk.CTkFrame(self.button_container)
        self.action_buttons_frame.pack(fill="x", pady=5)
        
        # Select Project Button (initially disabled)
        self.select_button = ctk.CTkButton(
            self.action_buttons_frame,
            text="Open Project",
            command=self.select_project,
            state="disabled",
            width=120
        )
        self.select_button.pack(side="left", padx=5)
        
        # Delete Project Button (initially disabled)
        self.delete_button = ctk.CTkButton(
            self.action_buttons_frame,
            text="Delete Project",
            command=lambda: self.delete_project(self.project_var.get()),
            state="disabled",
            fg_color="red",
            hover_color="#8B0000",  # Dark red for hover
            width=120
        )
        self.delete_button.pack(side="right", padx=5)
        
        # Load projects on init
        self.load_projects()
    
    def load_projects(self):
        """Load projects from database"""
        try:
            # Get projects from database using controller
            projects = self.controller.get_all_projects()
            
            if projects:
                # Update dropdown with project names
                project_names = [project['name'] for project in projects]
                self.project_dropdown.configure(values=project_names, state="normal")
                self.project_var.set(project_names[0])
                self.select_button.configure(state="normal")
                self.delete_button.configure(state="normal")  # Enable delete button
            else:
                # No projects available
                self.project_dropdown.configure(values=["No projects available"], state="disabled")
                self.project_var.set("No projects available")
                self.select_button.configure(state="disabled")
                self.delete_button.configure(state="disabled")  # Disable delete button
        except Exception as e:
            print(f"Error loading projects: {str(e)}")
            self.show_message("Error", f"Failed to load projects: {str(e)}")
    
    def center_dialog(self, dialog, width=400, height=200):
        """Center a dialog on the screen with given dimensions"""
        dialog.geometry(f"{width}x{height}")
        dialog.update_idletasks()  # Update "requested size" from geometry manager
        
        # Get screen dimensions
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        
        # Calculate x and y coordinates
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # Set the position of the dialog
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.transient(self)  # Make dialog modal
        dialog.grab_set()  # Make dialog modal
    
    def show_create_project_dialog(self):
        """Show dialog to create a new project"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Create New Project")
        self.center_dialog(dialog, width=400, height=320)
        
        # Project details container
        details_frame = ctk.CTkFrame(dialog)
        details_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Project Name
        ctk.CTkLabel(
            details_frame,
            text="Project Name:",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        name_var = ctk.StringVar()
        name_entry = ctk.CTkEntry(
            details_frame,
            textvariable=name_var,
            width=300
        )
        name_entry.pack(pady=(0, 15))
        
        # Project Description
        ctk.CTkLabel(
            details_frame,
            text="Description (optional):",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        description_text = ctk.CTkTextbox(
            details_frame,
            height=100,
            width=300
        )
        description_text.pack(pady=(0, 15))
        
        def create_project():
            name = name_var.get().strip()
            description = description_text.get("1.0", "end-1c").strip()
            
            if not name:
                self.show_message("Error", "Project name is required")
                return
            
            try:
                # Create project using controller
                project = self.controller.create_project(name, description)
                if project:
                    self.load_projects()  # Reload projects list
                    dialog.destroy()
                    self.show_message("Success", f"Project '{name}' created successfully!")
                    # Auto-select the newly created project
                    self.project_var.set(name)
                    self.select_project()
                else:
                    self.show_message("Error", "Failed to create project")
            except Exception as e:
                self.show_message("Error", f"Failed to create project: {str(e)}")
        
        # Buttons
        button_frame = ctk.CTkFrame(details_frame)
        button_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkButton(
            button_frame,
            text="Create",
            command=create_project
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side="right", padx=5)
    
    def select_project(self):
        """Handle project selection"""
        project_name = self.project_var.get()
        if project_name and project_name != "No projects available":
            try:
                # Get all projects to find the selected one
                projects = self.controller.get_all_projects()
                selected = next((p for p in projects if p['name'] == project_name), None)
                
                if selected:
                    global selected_project, project_id
                    selected_project = selected['name']
                    project_id = selected['project_id']
                    self.on_project_selected(selected_project)
                else:
                    self.show_message("Error", "Selected project not found")
            except Exception as e:
                print(f"Error selecting project: {str(e)}")
                self.show_message("Error", f"Failed to select project: {str(e)}")
    
    def show_message(self, title: str, message: str):
        """Show a message dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        self.center_dialog(dialog, width=300, height=150)
        
        ctk.CTkLabel(
            dialog,
            text=message,
            wraplength=250
        ).pack(pady=20)
        
        ctk.CTkButton(
            dialog,
            text="OK",
            command=dialog.destroy,
            width=100
        ).pack(pady=10)
    
    def delete_project(self, project_name):
        """Delete project with confirmation"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Delete Project")
        self.center_dialog(dialog, width=400, height=200)
        
        # Warning message
        warning_frame = ctk.CTkFrame(dialog)
        warning_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            warning_frame,
            text="⚠️ Warning",
            font=("Helvetica", 16, "bold"),
            text_color="red"
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            warning_frame,
            text=f"Are you sure you want to delete project '{project_name}'?\n\nThis action cannot be undone and will delete all associated components.",
            wraplength=300
        ).pack(pady=(0, 20))
        
        def confirm_delete():
            try:
                # Get project ID
                projects = self.controller.get_all_projects()
                project = next((p for p in projects if p['name'] == project_name), None)
                
                if project:
                    # Delete project and all its components
                    if self.controller.delete_project(project['project_id']):
                        dialog.destroy()
                        self.show_message("Success", f"Project '{project_name}' deleted successfully!")
                        self.load_projects()  # Refresh project list
                    else:
                        self.show_message("Error", "Failed to delete project")
                else:
                    self.show_message("Error", "Project not found")
                    
            except Exception as e:
                print(f"Error deleting project: {str(e)}")
                self.show_message("Error", f"Failed to delete project: {str(e)}")
            finally:
                dialog.destroy()
        
        # Button frame
        button_frame = ctk.CTkFrame(warning_frame)
        button_frame.pack(fill="x", pady=(0, 10))
        
        # Delete button
        ctk.CTkButton(
            button_frame,
            text="Delete Project",
            command=confirm_delete,
            fg_color="red",
            hover_color="#8B0000"  # Dark red for hover
        ).pack(side="left", padx=5)
        
        # Cancel button
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side="right", padx=5)