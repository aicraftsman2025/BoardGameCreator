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
        
        # Bottom Frame: Export Button, Progress Bar and Preview
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Left side: Export button and progress
        control_frame = ctk.CTkFrame(bottom_frame)
        control_frame.pack(side="left", fill="y", padx=5)
        
        # Export button
        ctk.CTkButton(
            control_frame,
            text="Start Export",
            command=self._start_export,
            width=120
        ).pack(pady=5)
        
        # Progress frame
        progress_frame = ctk.CTkFrame(control_frame)
        progress_frame.pack(fill="x", pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=5, pady=2)
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="Ready",
            font=("Arial", 10)
        )
        self.progress_label.pack(pady=2)
        
        # Preview frame
        self.preview_frame = ctk.CTkFrame(bottom_frame)
        self.preview_frame.pack(side="right", fill="both", expand=True, padx=5)
        
        ctk.CTkLabel(
            self.preview_frame,
            text="Preview",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.preview_container = ctk.CTkFrame(self.preview_frame)
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
        
        # Filter type selection (Column or Row Range)
        filter_type_var = ctk.StringVar(value="column")
        filter_type_menu = ctk.CTkOptionMenu(
            filter_frame,
            variable=filter_type_var,
            values=["column", "row range"],
            width=100,
            command=lambda x: self._update_filter_options(filter_frame, x)
        )
        filter_type_menu.pack(side="left", padx=2)
        
        # Column selection (initially visible)
        column_var = ctk.StringVar(value="Select column...")
        self.column_menu = ctk.CTkOptionMenu(
            filter_frame,
            variable=column_var,
            values=self._get_csv_columns(),
            width=150
        )
        self.column_menu.pack(side="left", padx=2)
        
        # Operator selection (initially visible)
        operator_var = ctk.StringVar(value="equals")
        self.operator_menu = ctk.CTkOptionMenu(
            filter_frame,
            variable=operator_var,
            values=["equals", "not equals", "contains", "greater than", "less than", "range"],
            width=100
        )
        self.operator_menu.pack(side="left", padx=2)
        
        # Value input
        value_var = ctk.StringVar()
        value_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=value_var,
            width=150,
            placeholder_text="Filter value... (use '-' for range)"
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
    
    def _update_filter_options(self, filter_frame, filter_type):
        """Update filter options based on filter type"""
        # Get the widgets
        widgets = filter_frame.winfo_children()
        column_menu = widgets[1]  # Column menu
        operator_menu = widgets[2]  # Operator menu
        
        if filter_type == "row range":
            # Hide column and operator menus
            column_menu.pack_forget()
            operator_menu.pack_forget()
        else:
            # Show column and operator menus
            column_menu.pack(side="left", padx=2, after=widgets[0])
            operator_menu.pack(side="left", padx=2, after=column_menu)
    
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
                        df = pd.read_csv(os.path.join("./assets_static/data", csv_file))
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
    
    def _apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply filters to DataFrame"""
        try:
            row_ranges = []
            
            for filter_frame in self.filters_container.winfo_children():
                widgets = filter_frame.winfo_children()
                filter_type = widgets[0].get()  # Filter type menu
                
                if filter_type == "row range":
                    value = widgets[3].get()  # Value entry for row range
                    try:
                        # Parse row range
                        if '-' in value:
                            start, end = map(int, value.split('-'))
                            # Convert to 0-based index and make end inclusive
                            start = max(0, start - 1)  # Convert 1-based to 0-based index
                            end = min(len(df), end)    # Ensure end doesn't exceed DataFrame length
                            row_ranges.append((start, end))
                        else:
                            # Single row number
                            row_num = int(value) - 1  # Convert to 0-based index
                            if 0 <= row_num < len(df):
                                row_ranges.append((row_num, row_num + 1))
                    except ValueError:
                        print(f"Invalid row range format: {value}")
                        continue
                else:
                    # Apply regular column filters
                    column = widgets[1].get()  # Column menu
                    operator = widgets[2].get()  # Operator menu
                    value = widgets[3].get()    # Value entry
                    
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
                        elif operator == "range":
                            try:
                                start, end = map(float, value.split('-'))
                                numeric_column = pd.to_numeric(df[column], errors='coerce')
                                df = df[(numeric_column >= start) & (numeric_column <= end)]
                            except ValueError:
                                print(f"Invalid range format: {value}")
                                continue
            
            # Apply row ranges if any exist
            if row_ranges:
                # Create a mask for selected rows
                mask = pd.Series(False, index=df.index)
                for start, end in row_ranges:
                    mask.iloc[start:end] = True
                df = df[mask]
            
            return df
            
        except Exception as e:
            print(f"Error applying filters: {e}")
            return df
    
    def _start_export(self):
        """Start the export process"""
        try:
            # Reset progress
            self.progress_bar.set(0)
            self.progress_label.configure(text="Starting export...")
            
            # Validation
            if not self._validate_export():
                return
            
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
            
            df = pd.read_csv(os.path.join("./assets_static/data", csv_file))
            
            # Apply filters
            df = self._apply_filters(df)
            if df.empty:
                self._show_error("No records match the filter criteria")
                return
            
            total_records = len(df)
            
            # Process each record
            for index, row in df.iterrows():
                # Update progress
                progress = (index + 1) / total_records
                self.progress_bar.set(progress)
                self.progress_label.configure(
                    text=f"Processing card {index + 1} of {total_records}"
                )
                self.update()  # Force GUI update
                
                # Create a copy of template data
                card_data = template_data.copy()
                
                # Apply mappings
                self._apply_mappings(card_data, row)
                
                # Generate filename
                filename = f"card_{index + 1}.png"
                export_path = os.path.join(self.path_var.get(), filename)
                
                # Generate card image
                success = self.template_controller.export_template_image(
                    template_data=card_data,
                    output_path=export_path,
                    preview_frame=self.preview_container
                )
                
                if not success:
                    self._show_error(f"Failed to generate card {index + 1}")
                    return
            
            # Update progress to complete
            self.progress_bar.set(1)
            self.progress_label.configure(text="Export completed!")
            self.update()
            
            tk.messagebox.showinfo("Success", "Export completed successfully!")
            
        except Exception as e:
            self._show_error(f"Export failed: {str(e)}")
        finally:
            # Reset progress
            self.progress_bar.set(0)
            self.progress_label.configure(text="Ready")
            self.update()
    
    def _apply_mappings(self, card_data: Dict, row: pd.Series):
        """Apply data mappings to card data"""
        try:
            mappings = card_data.get('data_source', {}).get('mappings', {})
            available_columns = row.index.tolist()
            
            for element_id, mapping in mappings.items():
                if mapping['type'] == 'direct':
                    column = mapping['column']
                    if column not in available_columns:
                        print(f"Warning: Column '{column}' not found in data")
                        continue
                    
                    value = str(row[column]) if pd.notna(row[column]) else ""
                    if not value:
                        continue
                    
                    for element in card_data['elements']:
                        if element['id'] == element_id and element['type'] == 'text':
                            element['properties']['text'] = value
                            break
                
                elif mapping['type'] == 'macro':
                    expression = mapping['expression']
                    for column in available_columns:
                        col_value = str(row[column]) if pd.notna(row[column]) else ""
                        expression = expression.replace(f"${{{column}}}", col_value)
                    
                    for element in card_data['elements']:
                        if element['id'] == element_id and element['type'] == 'image':
                            element['properties']['path'] = expression
                            break
        
        except Exception as e:
            print(f"Error applying mappings: {e}")
    
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