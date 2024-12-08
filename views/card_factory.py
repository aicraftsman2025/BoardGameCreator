import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import os
from typing import Dict, List

class CardFactory(ctk.CTkFrame):
    def __init__(self, parent, template_controller, csv_controller):
        super().__init__(parent)
        self.template_controller = template_controller
        self.csv_controller = csv_controller
        self.export_tasks = []
        
        self._create_ui()
        self._load_templates()
    
    def _create_ui(self):
        """Create the main UI layout"""
        # Top Frame: Template Selection and Export Path
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill="x", padx=10, pady=5)
        
        # Template Selection
        template_frame = ctk.CTkFrame(top_frame)
        template_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(
            template_frame,
            text="Select Template:",
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=5)
        
        self.template_var = ctk.StringVar(value="Select template...")
        self.template_menu = ctk.CTkOptionMenu(
            template_frame,
            variable=self.template_var,
            values=["Loading..."],
            command=self._on_template_selected,
            width=200
        )
        self.template_menu.pack(side="left", padx=5)
        
        # Export Path Selection
        path_frame = ctk.CTkFrame(top_frame)
        path_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(
            path_frame,
            text="Export Path:",
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=5)
        
        self.path_var = ctk.StringVar(value="Choose export path...")
        path_entry = ctk.CTkEntry(
            path_frame,
            textvariable=self.path_var,
            width=300,
            state="readonly"
        )
        path_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(
            path_frame,
            text="Browse",
            command=self._choose_export_path,
            width=100
        ).pack(side="left", padx=5)
        
        # Middle Frame: CSV Filter Configuration
        filter_frame = ctk.CTkFrame(self)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            filter_frame,
            text="CSV Filters",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.filters_container = ctk.CTkScrollableFrame(
            filter_frame,
            height=150
        )
        self.filters_container.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(
            filter_frame,
            text="+ Add Filter",
            command=self._add_filter,
            width=100
        ).pack(pady=5)
        
        # Bottom Frame: Task List and Preview
        bottom_container = ctk.CTkFrame(self)
        bottom_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Task frame (left side)
        task_frame = ctk.CTkFrame(bottom_container)
        task_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Task list header
        header_frame = ctk.CTkFrame(task_frame)
        header_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(
            header_frame,
            text="Export Tasks",
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            header_frame,
            text="Start Export",
            command=self._start_export,
            width=120
        ).pack(side="right", padx=5)
        
        # Task list
        self.task_list = ctk.CTkScrollableFrame(task_frame)
        self.task_list.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Preview frame (right side)
        preview_frame = ctk.CTkFrame(bottom_container)
        preview_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        preview_frame.configure(width=300)  # Set a default width
        
        # Preview header
        preview_header = ctk.CTkFrame(preview_frame)
        preview_header.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(
            preview_header,
            text="Preview",
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=5)
        
        # Preview canvas container with fixed dimensions
        self.preview_container = ctk.CTkFrame(preview_frame)
        self.preview_container.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _load_templates(self):
        """Load available templates"""
        templates = self.template_controller.get_all_templates()
        template_names = [t.name for t in templates] if templates else ["No templates"]
        self.template_menu.configure(values=template_names)
    
    def _choose_export_path(self):
        """Open dialog to choose export path"""
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)
    
    def _add_filter(self):
        """Add new CSV filter row"""
        filter_frame = ctk.CTkFrame(self.filters_container)
        filter_frame.pack(fill="x", padx=5, pady=2)
        
        # Column selection
        column_var = ctk.StringVar(value="Select column...")
        column_menu = ctk.CTkOptionMenu(
            filter_frame,
            variable=column_var,
            values=self._get_csv_columns(),
            width=150
        )
        column_menu.pack(side="left", padx=2)
        
        # Operator selection
        operator_var = ctk.StringVar(value="equals")
        operator_menu = ctk.CTkOptionMenu(
            filter_frame,
            variable=operator_var,
            values=["equals", "not equals", "contains", "greater than", "less than"],
            width=100
        )
        operator_menu.pack(side="left", padx=2)
        
        # Value input
        value_var = ctk.StringVar()
        value_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=value_var,
            width=150,
            placeholder_text="Filter value..."
        )
        value_entry.pack(side="left", padx=2)
        
        # Remove button
        ctk.CTkButton(
            filter_frame,
            text="×",
            width=30,
            command=lambda: filter_frame.destroy(),
            fg_color="red",
            hover_color="darkred"
        ).pack(side="right", padx=2)
    
    def _get_csv_columns(self) -> List[str]:
        """Get columns from selected template's CSV"""
        try:
            template_name = self.template_var.get()
            if template_name and template_name != "Select template...":
                template = next(t for t in self.template_controller.get_all_templates() 
                              if t.name == template_name)
                template_data = self.template_controller.load_template(template.id)
                if template_data and 'data_source' in template_data:
                    csv_file = template_data['data_source'].get('file')
                    if csv_file:
                        df = pd.read_csv(os.path.join("./assets/data", csv_file))
                        return list(df.columns)
            return ["No columns available"]
        except Exception:
            return ["Error loading columns"]
    
    def _on_template_selected(self, template_name: str):
        """Handle template selection"""
        # Update available columns in filters
        columns = self._get_csv_columns()
        for filter_frame in self.filters_container.winfo_children():
            for widget in filter_frame.winfo_children():
                if isinstance(widget, ctk.CTkOptionMenu):
                    widget.configure(values=columns)
        
        # Update preview container dimensions based on template
        try:
            template = next(t for t in self.template_controller.get_all_templates() 
                           if t.name == template_name)
            template_data = self.template_controller.load_template(template.id)
            
            if template_data and 'dimensions' in template_data:
                # Clear existing preview
                for widget in self.preview_container.winfo_children():
                    widget.destroy()
                
                # Get template dimensions
                width = template_data['dimensions']['width']
                height = template_data['dimensions']['height']
                bg_color = template_data.get('background_color', '#FFFFFF')
                
                # Configure preview container
                self.preview_container.configure(
                    width=width,
                    height=height,
                    fg_color=bg_color  # CustomTkinter uses fg_color for background
                )
                
                # Force update to apply new dimensions
                self.preview_container.update()
                
        except Exception as e:
            print(f"Error updating preview container: {e}")
    
    def _update_progress(self, progress):
        """Update progress bar safely"""
        try:
            if hasattr(self, 'progress_bar') and self.progress_bar.winfo_exists():
                self.progress_bar.set(progress)
                self.progress_bar.update()
        except Exception as e:
            print(f"Progress bar update failed: {e}")
    
    def _start_export(self):
        """Start the export process"""
        if not self._validate_export():
            return
        
        try:
            # Create export task frame
            task_frame = self._create_task_frame()
            progress_bar = task_frame.winfo_children()[1]  # Get progress bar
            status_label = task_frame.winfo_children()[2]  # Get status label
            
            # Store progress bar reference
            self.progress_bar = progress_bar
            
            def update_progress_safely(progress):
                self.after(0, lambda: self._update_progress(progress))
            
            # Get template data
            template_name = self.template_var.get()
            template = next(t for t in self.template_controller.get_all_templates() 
                          if t.name == template_name)
            template_data = self.template_controller.load_template(template.id)
            
            if not template_data.get('data_source'):
                self._show_error("Template has no data source configuration")
                return
            
            # Load CSV data
            csv_file = template_data['data_source'].get('file')
            if not csv_file:
                self._show_error("No CSV file configured in template")
                return
            
            df = pd.read_csv(os.path.join("./assets/data", csv_file))
            
            # Apply filters
            df = self._apply_filters(df)
            if df.empty:
                self._show_error("No records match the filter criteria")
                return
            
            # Update status
            total_records = len(df)
            status_label.configure(text=f"Processing 0/{total_records} records...")
            
            # Process each row
            progress = 0
            for index, row in df.iterrows():
                # Update progress
                progress = (index + 1) / total_records
                update_progress_safely(progress)
                status_label.configure(text=f"Processing {index + 1}/{total_records} records...")
                
                # Generate image for this record
                self._generate_card_image(template_data, row, index)
                
                # Force UI update
                self.update()
            
            # Complete
            progress = 1
            update_progress_safely(progress)
            status_label.configure(text=f"Completed: {total_records} cards exported")
            
        except Exception as e:
            self._show_error(f"Export failed: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply filters to DataFrame"""
        try:
            for filter_frame in self.filters_container.winfo_children():
                widgets = filter_frame.winfo_children()
                column = widgets[0].get()  # Column menu
                operator = widgets[1].get()  # Operator menu
                value = widgets[2].get()    # Value entry
                
                if column and operator and value:
                    if operator == "equals":
                        df = df[df[column] == value]
                    elif operator == "not equals":
                        df = df[df[column] != value]
                    elif operator == "contains":
                        df = df[df[column].astype(str).str.contains(value, case=False)]
                    elif operator == "greater than":
                        df = df[pd.to_numeric(df[column], errors='coerce') > float(value)]
                    elif operator == "less than":
                        df = df[pd.to_numeric(df[column], errors='coerce') < float(value)]
            
            return df
            
        except Exception as e:
            print(f"Error applying filters: {e}")
            return df
    
    def _generate_card_image(self, template_data: Dict, row: pd.Series, index: int):
        """Generate card image for a single record"""
        try:
            # Create a copy of template data
            card_data = template_data.copy()
            
            # Apply data mappings
            for element_id, mapping in template_data['data_source']['mappings'].items():
                if mapping['type'] == 'direct':
                    # Direct column mapping
                    column = mapping['column']
                    value = str(row[column])
                    
                    # Find and update element
                    for element in card_data['elements']:
                        if element['id'] == element_id:
                            if element['type'] == 'text':
                                element['properties']['text'] = value
                
                elif mapping['type'] == 'macro':
                    # Handle macro expressions
                    expression = mapping['expression']
                    # Replace column references with values
                    for column in row.index:
                        expression = expression.replace(f"${{{column}}}", str(row[column]))
                    
                    # Find and update element
                    for element in card_data['elements']:
                        if element['id'] == element_id:
                            if element['type'] == 'image':
                                element['properties']['path'] = expression
            
            # Generate filename
            filename = f"card_{index + 1}.png"
            export_path = os.path.join(self.path_var.get(), filename)
            self.preview_container.configure(
                width=template_data['dimensions']['width'],
                height=template_data['dimensions']['height']
            )

            self.preview_container.update()
            # Use template controller to render and save image
            success = self.template_controller.export_template_image(
                template_data=card_data,
                output_path=export_path,
                temp_window=self.preview_container
            )
            
            if not success:
                raise Exception("Failed to generate card image")
            
        except Exception as e:
            print(f"Error generating card {index + 1}: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_task_frame(self) -> ctk.CTkFrame:
        """Create a new task frame in the task list"""
        task_frame = ctk.CTkFrame(self.task_list)
        task_frame.pack(fill="x", padx=5, pady=2)
        
        # Task info
        info_frame = ctk.CTkFrame(task_frame)
        info_frame.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkLabel(
            info_frame,
            text=f"Template: {self.template_var.get()}",
            font=("Arial", 12)
        ).pack(side="left", padx=5)
        
        # Progress bar
        progress = ctk.CTkProgressBar(task_frame)
        progress.pack(fill="x", padx=5, pady=2)
        progress.set(0)
        
        # Status label
        status_label = ctk.CTkLabel(
            task_frame,
            text="Preparing...",
            font=("Arial", 10)
        )
        status_label.pack(side="left", padx=5)
        
        return task_frame
    
    def _validate_export(self) -> bool:
        """Validate export configuration"""
        if self.template_var.get() == "Select template...":
            self._show_error("Please select a template")
            return False
        
        if not self.path_var.get() or self.path_var.get() == "Choose export path...":
            self._show_error("Please select an export path")
            return False
        
        return True
    
    def _show_error(self, message: str):
        """Show error message"""
        tk.messagebox.showerror("Error", message) 