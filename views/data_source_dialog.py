import customtkinter as ctk
import tkinter as tk
import json
import pandas as pd
import os
import tkinter.messagebox as messagebox

# Create managers for rendering
from views.component_editor.canvas_manager import CanvasManager
from views.component_editor.events.event_manager import EventManager
from views.component_editor.element_manager import ElementManager

class DataSourceDialog:
    def __init__(self, parent, template_data, on_save):
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Mapping Fields")
        self.dialog.geometry("1000x800")
        self.template_data = template_data
        self.on_save = on_save
        
        self._create_ui()
        
    def _create_ui(self):
        """Create main UI layout"""
        # Main container
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left side: CSV Selection and Preview
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # CSV Selection at top of left frame
        self._create_csv_selector(left_frame)
        
        # Preview Panel below CSV selector
        self._create_preview_panel(left_frame)
        
        # Right side: Element Mapping
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="left", fill="y", padx=(5, 0), pady=5, ipadx=5)
        
        # Header label for mapping
        ctk.CTkLabel(
            right_frame,
            text="Element Mapping",
            font=("Arial", 14, "bold")
        ).pack(pady=(0,10))
        
        # Mapping frame with fixed width
        mapping_frame = ctk.CTkScrollableFrame(
            right_frame, 
            width=800,  # Fixed width for mapping panel
            height=600,  # Match preview height approximately
            fg_color="transparent"
        )
        mapping_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Get elements and columns
        elements = self.template_data.get('elements', [])
        columns = self._get_csv_columns(self.csv_var.get()) if self.csv_files else []
        
        # Create mapping UI
        self.mapping_vars = {}
        self.condition_frames = {}
        
        for element in elements:
            self._create_element_mapping_row(mapping_frame, element, columns)
        
        # Buttons at bottom of right frame
        self._create_button_panel(right_frame)
    
    def _create_csv_selector(self, parent):
        """Create CSV file selection"""
        csv_frame = ctk.CTkFrame(parent)
        csv_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(
            csv_frame,
            text="Select CSV File:",
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=5)
        
        self.csv_files = self._get_csv_files()
        self.csv_var = ctk.StringVar(value=self.csv_files[0] if self.csv_files else "No CSV files")
        
        self.csv_menu = ctk.CTkOptionMenu(
            csv_frame,
            values=self.csv_files if self.csv_files else ["No CSV files"],
            variable=self.csv_var,
            command=self._on_csv_selected,
            width=200
        )
        self.csv_menu.pack(side="left", padx=5)
    
    def _create_bottom_panel(self, parent):
        """Create bottom panel with mapping and buttons"""
        bottom_frame = ctk.CTkFrame(parent)
        bottom_frame.pack(fill="x", side="bottom", padx=5, pady=5)
        
        # Header label
        ctk.CTkLabel(
            bottom_frame,
            text="Element Mapping",
            font=("Arial", 14, "bold")
        ).pack(pady=(5,0))
        
        # Mapping frame with fixed height
        mapping_frame = ctk.CTkScrollableFrame(
            bottom_frame, 
            height=200,
            fg_color="transparent"
        )
        mapping_frame.pack(fill="x", padx=5, pady=5)
        
        # Get elements and columns
        elements = self.template_data.get('elements', [])
        columns = self._get_csv_columns(self.csv_var.get()) if self.csv_files else []
        
        # Create mapping UI
        self.mapping_vars = {}
        self.condition_frames = {}
        
        for element in elements:
            self._create_element_mapping_row(mapping_frame, element, columns)
        
        # Buttons frame
        self._create_button_panel(bottom_frame)
    
    def _create_element_mapping_row(self, parent, element, columns):
        """Create a single element mapping row"""
        # Main element frame with subtle border
        element_frame = ctk.CTkFrame(
            parent,
            fg_color=("gray95", "gray20"),
            border_width=1,
            border_color=("gray80", "gray30")
        )
        element_frame.pack(fill="x", padx=5, pady=2)
        
        # Top: Element info
        info_frame = ctk.CTkFrame(
            element_frame,
            fg_color="transparent"
        )
        info_frame.pack(fill="x", padx=5, pady=5)
        
        # Element ID and type
        ctk.CTkLabel(
            info_frame,
            text=f"ID: {element['id']}",
            font=("Arial", 12, "bold"),
            width=120,
            anchor="w"
        ).pack(side="left")
        
        ctk.CTkLabel(
            info_frame,
            text=f"Type: {element['type']}",
            font=("Arial", 11),
            width=100,
            anchor="w"
        ).pack(side="left", padx=5)
        
        # Bottom: Mapping controls
        mapping_frame = ctk.CTkFrame(
            element_frame,
            fg_color="transparent"
        )
        mapping_frame.pack(fill="x", expand=True, padx=5, pady=5)
        
        # Left side: Mapping type selector
        type_frame = ctk.CTkFrame(
            mapping_frame,
            fg_color="transparent"
        )
        type_frame.pack(side="left", padx=(0, 10))
        
        mapping_type_var = ctk.StringVar(value="direct")
        mapping_type = ctk.CTkOptionMenu(
            type_frame,
            values=["direct", "conditional", "macro"],
            variable=mapping_type_var,
            width=100,
            command=lambda t, eid=element['id']: self._on_mapping_type_changed(t, eid)
        )
        mapping_type.pack()
        
        # Right side: Options frame for different mapping types
        options_frame = ctk.CTkFrame(
            mapping_frame,
            fg_color="transparent"
        )
        options_frame.pack(side="left", fill="x", expand=True)
        
        # Create frames for each mapping type
        direct_frame = self._create_direct_mapping_frame(options_frame, columns)
        condition_frame = self._create_conditional_mapping_frame(options_frame, element['id'])
        macro_frame = self._create_macro_mapping_frame(options_frame)
        
        # Initially show direct mapping and hide others
        direct_frame.pack(fill="x")
        condition_frame.pack_forget()
        macro_frame.pack_forget()
        
        # Store references
        self.mapping_vars[element['id']] = {
            'type': mapping_type_var,
            'frames': {
                'direct': direct_frame,
                'conditional': condition_frame,
                'macro': macro_frame
            },
            'column': direct_frame.column_var,
            'conditions': [],
            'macro': macro_frame.macro_var
        }
        
        self.condition_frames[element['id']] = {
            'frame': condition_frame,
            'conditions': []
        }
    
    def _create_direct_mapping_frame(self, parent, columns):
        """Create direct mapping frame"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        
        # Store column variable in the frame
        frame.column_var = ctk.StringVar(value="Column...")
        
        ctk.CTkOptionMenu(
            frame,
            values=["None"] + columns,
            variable=frame.column_var,
            width=100
        ).pack(side="left", padx=5)
        
        return frame
    
    def _create_conditional_mapping_frame(self, parent, element_id):
        """Create conditional mapping frame"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        
        # Container for conditions
        conditions_container = ctk.CTkFrame(frame, fg_color="transparent")
        conditions_container.pack(fill="x", expand=True)
        
        # Store reference to container
        frame.conditions_container = conditions_container
        
        # Add condition button
        ctk.CTkButton(
            frame,
            text="+ Add Condition",
            width=120,
            height=28,
            command=lambda: self._add_condition(element_id)
        ).pack(pady=(0, 5))
        
        return frame
    
    def _create_macro_mapping_frame(self, parent):
        """Create macro mapping frame"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        
        # Store macro variable in the frame
        frame.macro_var = ctk.StringVar()
        
        entry = ctk.CTkEntry(
            frame,
            textvariable=frame.macro_var,
            width=300,
            placeholder_text="Enter macro (e.g., ${column1} + ' ' + ${column2})"
        )
        entry.pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame,
            text="?",
            width=30,
            command=self._show_macro_help
        ).pack(side="left", padx=2)
        
        return frame
    
    def _on_mapping_type_changed(self, mapping_type, element_id):
        """Handle mapping type change"""
        try:
            # If switching to conditional, ensure container exists
            if mapping_type == "conditional":
                condition_data = self.condition_frames[element_id]
                if not hasattr(condition_data['frame'], 'conditions_container'):
                    condition_data['frame'].conditions_container = ctk.CTkFrame(
                        condition_data['frame'],
                        fg_color="transparent"
                    )
                    condition_data['frame'].conditions_container.pack(fill="x", expand=True)
            
            self._show_mapping_type(mapping_type, element_id)
            
        except Exception as e:
            print(f"Error changing mapping type: {e}")
            import traceback
            traceback.print_exc()
    
    def _show_mapping_type(self, mapping_type, element_id):
        """Show/hide mapping UI based on type"""
        try:
            mapping_data = self.mapping_vars[element_id]
            frames = mapping_data['frames']
            
            # Hide all frames
            for frame in frames.values():
                if isinstance(frame, (ctk.CTkFrame, tk.Frame)) and frame.winfo_exists():
                    frame.pack_forget()
            
            # Show selected frame
            if mapping_type in frames:
                frame = frames[mapping_type]
                if isinstance(frame, (ctk.CTkFrame, tk.Frame)) and frame.winfo_exists():
                    frame.pack(fill="x", padx=5, pady=2)
                    
        except Exception as e:
            print(f"Error switching mapping type: {e}")
            import traceback
            traceback.print_exc()
    
    def _add_condition(self, element_id):
        """Add new condition to element mapping"""
        condition_data = self.condition_frames[element_id]
        columns = self._get_csv_columns(self.csv_var.get())
        
        # Create condition frame
        condition = ctk.CTkFrame(condition_data['frame'].conditions_container)
        condition.pack(fill="x", padx=5, pady=2)
        
        # Store condition variables
        condition_vars = {
            'column': ctk.StringVar(value="Column..."),
            'operator': ctk.StringVar(value="equals"),
            'value': ctk.StringVar(),
            'result': ctk.StringVar(),
            'frame': condition  # Store frame reference
        }
        
        # Column selector
        column_menu = ctk.CTkOptionMenu(
            condition,
            values=columns,
            variable=condition_vars['column'],
            width=80
        )
        column_menu.pack(side="left", padx=1)
        
        # Operator selector
        operator_menu = ctk.CTkOptionMenu(
            condition,
            values=["equals", "not equals", "contains", "greater than", "less than"],
            variable=condition_vars['operator'],
            width=80
        )
        operator_menu.pack(side="left", padx=2)
        
        # Value input
        value_entry = ctk.CTkEntry(
            condition,
            textvariable=condition_vars['value'],
            width=80,
            placeholder_text="Value"
        )
        value_entry.pack(side="left", padx=2)
        
        # Result value input
        result_entry = ctk.CTkEntry(
            condition,
            textvariable=condition_vars['result'],
            width=80,
            placeholder_text="Result"
        )
        result_entry.pack(side="left", padx=2)
        
        # Remove button
        ctk.CTkButton(
            condition,
            text="×",
            width=20,
            height=20,
            fg_color="red",
            hover_color="darkred",
            font=("Arial", 12, "bold"),
            command=lambda: self._remove_condition(element_id, condition_vars)
        ).pack(side="left", padx=1)
        
        # Add condition to list
        self.mapping_vars[element_id]['conditions'].append(condition_vars)
    
    def _remove_condition(self, element_id, condition_vars):
        """Remove single condition from element mapping"""
        try:
            # Remove the condition frame
            if condition_vars['frame'].winfo_exists():
                condition_vars['frame'].destroy()
            
            # Remove condition from the list
            conditions = self.mapping_vars[element_id]['conditions']
            if condition_vars in conditions:
                conditions.remove(condition_vars)
                
        except Exception as e:
            print(f"Error removing condition: {e}")
            import traceback
            traceback.print_exc()
    
    def _save_mapping(self):
        """Save the mapping configuration"""
        try:
            mapping = {}
            for element_id, vars in self.mapping_vars.items():
                mapping_type = vars['type'].get()
                
                if mapping_type == "direct":
                    if vars['column'].get() not in ["None", "Select column..."]:
                        mapping[element_id] = {
                            'type': 'direct',
                            'column': vars['column'].get()
                        }
                
                elif mapping_type == "conditional":
                    conditions = []
                    for condition in vars['conditions']:
                        if all(condition[k].get() for k in ['column', 'operator', 'value', 'result']):
                            conditions.append({
                                'column': condition['column'].get(),
                                'operator': condition['operator'].get(),
                                'value': condition['value'].get(),
                                'result': condition['result'].get()
                            })
                    if conditions:
                        mapping[element_id] = {
                            'type': 'conditional',
                            'conditions': conditions
                        }
                
                elif mapping_type == "macro":
                    if vars['macro'].get():
                        mapping[element_id] = {
                            'type': 'macro',
                            'expression': vars['macro'].get()
                        }
            
            data_source = {
                'type': 'csv',
                'file': self.csv_var.get(),
                'mappings': mapping
            }
            
            self.on_save(data_source)
            self.dialog.destroy()
            
        except Exception as e:
            print(f"Error saving mapping: {e}")
            messagebox.showerror("Error", f"Failed to save mapping: {str(e)}")
    
    def _on_csv_selected(self, csv_file):
        """Handle CSV file selection"""
        try:
            # Update column options in mapping dropdowns
            columns = self._get_csv_columns(csv_file)
            for var in self.mapping_vars.values():
                menu = var._optionmenu_callback._menu
                menu.configure(values=["None"] + columns)
                if var.get() not in ["None"] + columns:
                    var.set("None")
                    
        except Exception as e:
            print(f"Error updating CSV columns: {e}")
            messagebox.showerror("Error", f"Failed to load CSV columns: {str(e)}")    
    def _get_csv_files(self):
        try:
            data_dir = "./assets_static/data"
            return [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        except Exception:
            return []
    
    def _get_csv_columns(self, csv_file):
        try:
            data_path = os.path.join("./assets_static/data", csv_file)
            df = pd.read_csv(data_path)
            return list(df.columns)
        except Exception:
            return []
    
    def _create_preview_panel(self, parent):
        """Create template preview panel with element IDs"""
        preview_frame = ctk.CTkFrame(parent)
        preview_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create managers for rendering
        from views.component_editor.canvas_manager import CanvasManager
        from views.component_editor.events.event_manager import EventManager
        from views.component_editor.element_manager import ElementManager
        
        # Create managers for preview
        self.event_manager = EventManager()
        self.element_manager = ElementManager(
            event_manager=self.event_manager,
            parent_window=self.dialog,
            asset_controller=None
        )
        
        # Create temporary canvas manager for rendering with disabled interactions
        self.temp_canvas_manager = CanvasManager(
            preview_frame,
            self.event_manager,
            self.element_manager
        )
        
        # Disable all mouse bindings on the temporary canvas
        self.temp_canvas_manager.canvas.unbind('<Button-1>')
        self.temp_canvas_manager.canvas.unbind('<B1-Motion>')
        self.temp_canvas_manager.canvas.unbind('<ButtonRelease-1>')
        self.temp_canvas_manager.canvas.unbind('<Double-Button-1>')
        self.temp_canvas_manager.canvas.unbind('<Button-3>')
        self.temp_canvas_manager.canvas.unbind('<Control-c>')
        self.temp_canvas_manager.canvas.unbind('<Control-v>')
        self.temp_canvas_manager.canvas.unbind('<Delete>')
        
        # Make temporary canvas non-interactive
        self.temp_canvas_manager.canvas.configure(state="disabled")
        
        # Initial render
        self._update_preview()
    
    def _update_preview(self):
        """Update the template preview"""
        try:
            # Get elements from template data
            elements = self.template_data.get('elements', [])
            
            # Set canvas properties from template
            properties = self.template_data.get('properties', {})
            self.temp_canvas_manager.background_color = properties.get('background_color', '#FFFFFF')
            
            # Get rendered canvas from temp canvas manager
            rendered_canvas = self.temp_canvas_manager.render_elements_ondemand(elements)
            
        except Exception as e:
            print(f"Error updating preview: {e}")
            import traceback
            traceback.print_exc()
    
    def _show_macro_help(self):
        """Show macro usage examples"""
        help_dialog = ctk.CTkToplevel(self.dialog)
        help_dialog.title("Macro Usage Examples")
        help_dialog.geometry("600x400")
        
        # Create scrollable text
        text = ctk.CTkTextbox(help_dialog)
        text.pack(fill="both", expand=True, padx=10, pady=10)
        
        help_text = """
Macro Usage Examples:

1. Basic Column Reference:
   ${column_name}
   Example: ${first_name}
   Result: "John"

2. Concatenation:
   ${first_name} ${last_name}
   Result: "John Doe"

3. With Static Text:
   "Name: ${first_name} ${last_name}"
   Result: "Name: John Doe"

4. Conditional Text:
   "Status: " + ("Active" if ${status} == "active" else "Inactive")
   Result: "Status: Active"

5. String Operations:
   ${first_name}.upper() + " " + ${last_name}.lower()
   Result: "JOHN doe"

6. Multiple Columns:
   "${first_name} ${last_name} (${age} years old)"
   Result: "John Doe (30 years old)"

7. Basic Arithmetic:
   "Age in 5 years: ${age} + 5"
   Result: "Age in 5 years: 35"

Notes:
- Use ${column_name} to reference CSV columns
- Supports basic Python expressions
- String operations: .upper(), .lower(), .title()
- Can combine multiple columns and static text
- Supports basic arithmetic for numeric columns
"""
        
        text.insert("1.0", help_text)
        text.configure(state="disabled")
        
        # Close button
        ctk.CTkButton(
            help_dialog,
            text="Close",
            command=help_dialog.destroy
        ).pack(pady=10)
    
    def _create_button_panel(self, parent):
        """Create bottom buttons panel"""
        btn_frame = ctk.CTkFrame(parent)
        btn_frame.pack(fill="x", padx=5, pady=5)
        
        # Save button
        ctk.CTkButton(
            btn_frame,
            text="Save Mapping",
            command=self._save_mapping,
            width=120,
            height=32,
            font=("Arial", 12)
        ).pack(side="left", padx=5)
        
        # Cancel button
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.dialog.destroy,
            width=100,
            height=32,
            font=("Arial", 12)
        ).pack(side="right", padx=5)
    
