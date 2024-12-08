import customtkinter as ctk
import json
from typing import Optional, Dict
import pandas as pd
import os

class TemplateManager(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_template = None
        
        self._create_toolbar()
        self._create_template_list()
        
        # Load initial templates
        self.load_templates()
    
    def _create_toolbar(self):
        """Create toolbar with essential buttons"""
        self.toolbar = ctk.CTkFrame(self)
        self.toolbar.pack(fill="x", padx=5, pady=5)
        
        # Create Template Button (Updated command)
        self.create_btn = ctk.CTkButton(
            self.toolbar,
            text="Create Template",
            command=self.show_create_template_dialog  # Changed from create_template_item
        )
        self.create_btn.pack(side="left", padx=5)
        
        # Search Entry
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.filter_templates())
        self.search_entry = ctk.CTkEntry(
            self.toolbar,
            placeholder_text="Search templates...",
            textvariable=self.search_var,
            width=200
        )
        self.search_entry.pack(side="right", padx=5)
    
    def _create_template_list(self):
        """Create scrollable template list"""
        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    def show_create_template_dialog(self):
        """Show dialog to create a new template"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Create New Template")
        dialog.geometry("400x200")
        
        # Template name input
        name_frame = ctk.CTkFrame(dialog)
        name_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            name_frame,
            text="Template Name:"
        ).pack(side="left", padx=5)
        
        name_var = ctk.StringVar()
        name_entry = ctk.CTkEntry(
            name_frame,
            textvariable=name_var,
            width=200
        )
        name_entry.pack(side="right", padx=5)
        
        def save_template():
            name = name_var.get().strip()
            if not name:
                self.show_message("Error", "Template name is required")
                return
                
            # Updated to match controller method signature
            if self.controller.create_template(name):  # Removed the empty dict argument
                self.show_message("Success", "Template created successfully!")
                self.load_templates()
                dialog.destroy()
            else:
                self.show_message("Error", "Failed to create template")
        
        # Buttons
        btn_frame = ctk.CTkFrame(dialog)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Create",
            command=save_template
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side="right", padx=5)
    
    def display_template_item(self, template):
        """Display a template item in the list"""
        frame = ctk.CTkFrame(self.list_frame)
        frame.pack(fill="x", padx=5, pady=2)
        
        # Template name and last modified
        info_frame = ctk.CTkFrame(frame)
        info_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(
            info_frame,
            text=template.name,
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=5)
        
        ctk.CTkLabel(
            info_frame,
            text=f"Modified: {template.updated_at.strftime('%Y-%m-%d %H:%M')}",
            font=("Arial", 10)
        ).pack(side="right", padx=5)
        
        # Action buttons
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        ctk.CTkButton(
            btn_frame,
            text="Edit JSON",
            command=lambda t=template: self.edit_template_json(t),
            width=80
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_frame,
            text="Mapping Fields",
            command=lambda t=template: self._show_data_source_dialog(t),
            width=100
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_frame,
            text="Delete",
            command=lambda t=template: self.delete_template(t.id),
            fg_color="red",
            width=80
        ).pack(side="right", padx=2)
    
    def edit_template_json(self, template):
        """Edit template JSON data"""
        # Load full template data
        template_data = self.controller.load_template(template.id)
        if not template_data:
            self.show_message("Error", "Failed to load template data")
            return
        
        # Create edit dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Edit Template: {template.name}")
        dialog.geometry("600x800")
        
        # JSON editor
        editor_frame = ctk.CTkFrame(dialog)
        editor_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # JSON text area
        json_text = ctk.CTkTextbox(editor_frame, wrap="none")
        json_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Insert formatted JSON
        formatted_json = json.dumps(template_data, indent=2)
        json_text.insert("1.0", formatted_json)
        
        def save_json():
            try:
                # Parse JSON to validate
                new_data = json.loads(json_text.get("1.0", "end-1c"))
                
                # Update template
                if self.controller.update_template(template.id, new_data):
                    self.show_message("Success", "Template updated successfully!")
                    self.load_templates()
                    dialog.destroy()
                else:
                    self.show_message("Error", "Failed to update template")
            except json.JSONDecodeError as e:
                self.show_message("Invalid JSON", f"Error: {str(e)}")
        
        # Control buttons
        btn_frame = ctk.CTkFrame(dialog)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Save",
            command=save_json
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side="right", padx=5)
        
        def add_data_source():
            """Add CSV data source to template"""
            try:
                # Get current template data from editor
                template_data = json.loads(json_text.get("1.0", "end-1c"))
                
                # Create data source dialog
                from views.data_source_dialog import DataSourceDialog
                
                def on_save(mapping_config):
                    # Update template JSON with mapping
                    template_data["data_source"] = mapping_config
                    
                    # Update text area
                    json_text.delete("1.0", "end")
                    json_text.insert("1.0", json.dumps(template_data, indent=2))
                
                # Show dialog
                DataSourceDialog(self, template_data, on_save)
                
            except Exception as e:
                self.show_message("Error", f"Failed to Mapping Fields: {str(e)}")
        
        # Mapping Fields button
        ctk.CTkButton(
            btn_frame,
            text="Mapping Fields",
            command=add_data_source
        ).pack(side="left", padx=5)
    def load_templates(self):
        """Load and display all templates"""
        # Clear existing list
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        # Get templates
        templates = self.controller.get_all_templates()
        
        if not templates:
            ctk.CTkLabel(
                self.list_frame,
                text="No templates found",
                font=("Arial", 12)
            ).pack(pady=20)
            return
        
        # Filter if search text exists
        search_text = self.search_var.get().lower()
        if search_text:
            templates = [t for t in templates if search_text in t.name.lower()]
        
        # Create template items
        for template in templates:
            self.display_template_item(template)
    
    def filter_templates(self):
        """Filter templates based on search text"""
        self.load_templates()
    
    def show_message(self, title: str, message: str):
        """Show a message dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("300x150")
        
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
        
    def delete_template(self, template_id: str):
        """Delete a template with confirmation"""
        # Create confirmation dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Delete")
        dialog.geometry("300x150")
        
        # Warning message
        ctk.CTkLabel(
            dialog,
            text="Are you sure you want to delete this template?\nThis action cannot be undone.",
            wraplength=250
        ).pack(pady=20)
        
        # Button frame
        btn_frame = ctk.CTkFrame(dialog)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        def confirm_delete():
            # Delete template
            if self.controller.delete_template(template_id):
                self.show_message("Success", "Template deleted successfully!")
                self.load_templates()  # Refresh template list
                dialog.destroy()
            else:
                self.show_message("Error", "Failed to delete template")
                dialog.destroy()
        
        # Confirm button
        ctk.CTkButton(
            btn_frame,
            text="Delete",
            command=confirm_delete,
            fg_color="red",
            hover_color="#8B0000"  # Dark red for hover
        ).pack(side="left", padx=5)
        
        # Cancel button
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side="right", padx=5)
    
    def _show_data_source_dialog(self, template):
        """Show dialog for adding data source to template"""
        try:
            # Load full template data
            template_data = self.controller.load_template(template.id)
            if not template_data:
                self.show_message("Error", "Failed to load template data")
                return
            
            # Import and show data source dialog
            from views.data_source_dialog import DataSourceDialog
            DataSourceDialog(
                self,
                template_data,
                lambda data_source: self._save_data_source(template.id, data_source)
            )
            
        except Exception as e:
            print(f"Error showing data source dialog: {e}")
            self.show_message("Error", f"Failed to show data source dialog: {str(e)}")
    
    def _save_data_source(self, template_id, data_source):
        """Save data source configuration to template"""
        try:
            # Load current template data
            template_data = self.controller.load_template(template_id)
            if not template_data:
                raise Exception("Failed to load template data")
            
            # Add/update data source configuration
            template_data['data_source'] = data_source
            
            # Save updated template
            if self.controller.update_template(template_id, template_data):
                self.show_message("Success", "Data source configuration saved successfully!")
            else:
                raise Exception("Failed to save template data")
                
        except Exception as e:
            print(f"Error saving data source: {e}")
            self.show_message("Error", f"Failed to save data source: {str(e)}")