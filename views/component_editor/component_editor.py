import customtkinter as ctk
from .events.event_manager import EventManager
from .events.event_types import EventType
from .toolbar import Toolbar
from .properties_panel import PropertiesPanel
from .canvas_manager import CanvasManager
from .element_manager import ElementManager
from .history_manager import HistoryManager
from PIL import Image, ImageDraw
import qrcode
from utils.image_processor import ImageProcessor
import tkinter as tk
import os
import json
import tkinter.messagebox as messagebox

class ComponentEditor(ctk.CTkFrame):
    def __init__(self, parent, component_controller, template_controller, asset_controller):
        super().__init__(parent)
        
        # Initialize controllers
        self.component_controller = component_controller
        self.template_controller = template_controller
        self.asset_controller = asset_controller

        # Configure frame to expand
        self.pack(fill="both", expand=True)
        
        # Create event manager
        self.event_manager = EventManager()
        
        # Initialize managers
        self.element_manager = ElementManager(
            event_manager=self.event_manager,
            parent_window=self.winfo_toplevel(),
            asset_controller=asset_controller
        )
        
        # Create toolbar at the top (before main container)
        self.toolbar = Toolbar(self, self.event_manager)
        self.toolbar.pack(fill="x", padx=5, pady=(5, 0))  # Adjusted padding
        
        # Create main horizontal container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create canvas container (left side)
        self.canvas_container = ctk.CTkFrame(self.main_container)
        self.canvas_container.pack(side="left", fill="both", expand=True)
        
        # Create canvas manager
        self.canvas_manager = CanvasManager(
            self.canvas_container, 
            self.event_manager,
            self.element_manager
        )
        self.canvas_manager.get_frame().pack(fill="both", expand=True)
        
        # Create properties panel (right side)
        self.properties_panel = PropertiesPanel(self.main_container, self.event_manager)
        self.properties_panel.pack(
            side="right", 
            fill="y",
            padx=(5, 5),
            pady=5
        )
        
        # Initialize state variables
        self.selected_element = None
        self.resize_start = None
        self.original_size = None
        self.move_start = None
        
        # Add history manager
        self.history_manager = HistoryManager(self.event_manager)
        self.history_manager.push_state([], "#FFFFFF")
        
        # Initialize keyboard shortcuts
        self.shortcuts = {
            'm': 'move',
            'r': 'resize',
            'delete': 'delete',
            'backspace': 'delete',
            'Control-z': 'undo',
            'Control-y': 'redo',
            'Control-Shift-Z': 'redo'
        }
        
        # Subscribe to events
        self._subscribe_to_events()
        
        # Initialize keyboard shortcuts
        self._setup_shortcuts()
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts for tools"""
        # Bind keyboard events to canvas
        self.canvas_manager.canvas.bind('<Key>', self._handle_shortcut)
        # Ensure canvas can receive keyboard focus
        self.canvas_manager.canvas.focus_set()
    
    def _handle_shortcut(self, event):
        """Handle keyboard shortcuts only when an element is selected"""
        if not self.selected_element:
            return
            
        key = event.keysym.lower()
        
        if key in self.shortcuts:
            action = self.shortcuts[key]
            
            if action == 'delete':
                self.element_manager.delete_element(self.selected_element)
            else:
                self.toolbar._select_tool(action)
            
            return "break"
    
    def _subscribe_to_events(self):
        """Subscribe to all relevant events"""
        # Canvas events
        self.event_manager.subscribe(EventType.CANVAS_CLICKED, self._handle_canvas_click)
        self.event_manager.subscribe(EventType.CANVAS_DRAGGED, self._handle_canvas_drag)
        self.event_manager.subscribe(EventType.CANVAS_RELEASED, self._handle_canvas_release)
        
        # Element events
        self.event_manager.subscribe(EventType.ELEMENT_CREATED, self._handle_element_created)
        self.event_manager.subscribe(EventType.ELEMENT_SELECTED, self._handle_element_selected)
        self.event_manager.subscribe(EventType.ELEMENT_DELETED, self._handle_element_deleted)
        self.event_manager.subscribe(EventType.ELEMENT_MOVED, self._handle_element_moved)
        self.event_manager.subscribe(EventType.ELEMENT_RESIZED, self._handle_element_resized)
        
        # Tool events
        self.event_manager.subscribe(EventType.TOOL_CHANGED, self._handle_tool_changed)
        
        # Template events
        self.event_manager.subscribe(EventType.TEMPLATE_ACTION, self._handle_template_action)
        
        # Save events
        self.event_manager.subscribe(EventType.SAVE_COMPONENT, self._handle_save_component)
        
        # Undo/Redo events
        self.event_manager.subscribe(EventType.UNDO, self._handle_undo)
        self.event_manager.subscribe(EventType.REDO, self._handle_redo)
        
        # Add subscription for element editing
        self.event_manager.subscribe(
            EventType.ELEMENT_EDITED,
            self._handle_element_edited
        )
        
        # Export events
        self.event_manager.subscribe(EventType.EXPORT_COMPONENT, self._handle_export_component)
    
    def _handle_canvas_click(self, data):
        """Handle canvas click events"""
        tool = self.toolbar.get_current_tool()
        clicked_element = data.get('element')
        
        if tool in ['select', 'move', 'resize']:
            if clicked_element:
                self.selected_element = clicked_element
                self.event_manager.emit(EventType.ELEMENT_SELECTED, clicked_element)
                self.canvas_manager.show_selection(clicked_element)
                
                if tool == 'resize':
                    self.resize_start = (data['x'], data['y'])
                    self.original_size = (
                        clicked_element.get('properties', {}).get('width', 100),
                        clicked_element.get('properties', {}).get('height', 100)
                    )
                elif tool == 'move':
                    self.move_start = (
                        data['x'] - clicked_element.get('x', 0),
                        data['y'] - clicked_element.get('y', 0)
                    )
            else:
                self.selected_element = None
                self.event_manager.emit(EventType.ELEMENT_DESELECTED, None)
                self.canvas_manager.clear_selection()
        
        elif tool in ['text', 'shape', 'image', 'qrcode']:
            # Create new element
            new_element = self.element_manager.create_element(tool, data['x'], data['y'])
            
            # Open the appropriate dialog
            if tool == 'text':
                self.element_manager.edit_text_element(new_element)
            elif tool == 'shape':
                self.element_manager.edit_shape_element(new_element)
            elif tool == 'image':
                self.element_manager.edit_image_element(new_element)
            elif tool == 'qrcode':
                self.element_manager.edit_qrcode_element(new_element)
    
    def _handle_canvas_drag(self, data):
        """Handle canvas drag events"""
        if not self.selected_element:
            return
        
        tool = self.toolbar.get_current_tool()
        
        if tool == 'move':
            # Update element position
            new_x = data['x'] - self.move_start[0]
            new_y = data['y'] - self.move_start[1]
            
            self.selected_element['x'] = new_x
            self.selected_element['y'] = new_y
            
            # Re-render and show selection
            self.canvas_manager.render_elements(self.element_manager.elements)
            
        elif tool == 'resize':
            if self.resize_start and self.original_size:
                dx = data['x'] - self.resize_start[0]
                dy = data['y'] - self.resize_start[1]
                
                # Ensure minimum size
                new_width = max(20, self.original_size[0] + dx)
                new_height = max(20, self.original_size[1] + dy)
                
                self.selected_element['properties']['width'] = new_width
                self.selected_element['properties']['height'] = new_height
                
                # Re-render and show selection
                self.canvas_manager.render_elements(self.element_manager.elements)
    
    def _handle_canvas_release(self, data):
        """Handle canvas release events"""
        if self.selected_element:
            if self.move_start or self.resize_start:
                # Push state to history after moving or resizing
                self.history_manager.push_state(
                    self.element_manager.elements,
                    self.canvas_manager.background_color
                )
                self.event_manager.emit(EventType.ELEMENT_EDITED, self.selected_element)
            
        self.move_start = None
        self.resize_start = None
        self.original_size = None
    
    def _handle_element_created(self, element):
        """Handle element creation"""
        self.toolbar._select_tool('select')
        self.selected_element = element
        self.event_manager.emit(EventType.ELEMENT_SELECTED, element)
        # Push state to history after element creation
        self.history_manager.push_state(
            self.element_manager.elements,
            self.canvas_manager.background_color
        )
        self.canvas_manager.render_elements(self.element_manager.elements)
    
    def _handle_element_selected(self, element):
        """Handle element selection"""
        self.selected_element = element
        self.canvas_manager.show_selection(element)
    
    def _handle_element_deleted(self, element):
        """Handle element deletion"""
        if element == self.selected_element:
            self.selected_element = None
        self.canvas_manager.clear_selection()
        # Push state to history after deletion
        self.history_manager.push_state(
            self.element_manager.elements,
            self.canvas_manager.background_color
        )
    
    def _handle_element_moved(self, element):
        """Handle element movement"""
        if element == self.selected_element:
            self.canvas_manager.show_selection(element)
    
    def _handle_element_resized(self, element):
        """Handle element resizing"""
        if element == self.selected_element:
            self.canvas_manager.show_selection(element)
    
    def _handle_tool_changed(self, data):
        """Handle tool changes"""
        if data['tool'] not in ['move', 'resize']:
            self.move_start = None
            self.resize_start = None
            self.original_size = None
    
    def _handle_template_action(self, action):
        """Handle template actions"""
        if action == "Load Template":
            self.template_controller.load_template()
        elif action == "Save as Template":
            self.template_controller.save_as_template()
        elif action == "Manage Templates":
            self.template_controller.show_template_manager()
    
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
        dialog.transient(self.winfo_toplevel())  # Make dialog modal
        dialog.grab_set()  # Make dialog modal
    
    def _handle_save_component(self, data):
        """Handle component save"""
        try:
            # Check if we're editing an existing component
            existing_component = getattr(self, 'current_component', None)
            print(f"Existing component: {existing_component}")
            if existing_component:
                # Update existing component
                try:
                    # Calculate actual dimensions based on unit and DPI
                    width_px = data['dimensions']['width']
                    height_px = data['dimensions']['height']
                    
                    if data['unit'] == 'mm':
                        # Convert mm to inches then to pixels
                        width_px = int((data['dimensions']['width'] / 25.4) * data['dpi'])
                        height_px = int((data['dimensions']['height'] / 25.4) * data['dpi'])
                    elif data['unit'] == 'cm':
                        # Convert cm to inches then to pixels
                        width_px = int((data['dimensions']['width'] / 2.54) * data['dpi'])
                        height_px = int((data['dimensions']['height'] / 2.54) * data['dpi'])
                    elif data['unit'] == 'in':
                        # Convert inches to pixels
                        width_px = int(data['dimensions']['width'] * data['dpi'])
                        height_px = int(data['dimensions']['height'] * data['dpi'])
                    
                    # Store all component data in properties
                    properties = {
                        'width': data['dimensions']['width'],
                        'height': data['dimensions']['height'],
                        'unit': data['unit'],
                        'dpi': data['dpi'],
                        'elements': self.element_manager.elements,
                        'background_color': self.canvas_manager.background_color,
                        'dimensions': {
                            'actual_width': width_px,
                            'actual_height': height_px,
                            'width': data['dimensions']['width'],
                            'height': data['dimensions']['height'],
                            'unit': data['unit']
                        }
                    }
                    
                    # Update component data
                    component_data = {
                        'name': existing_component['name'],
                        'type': existing_component['type'],
                        'properties': properties
                    }
                    
                    # Update component in database
                    self.component_controller.update_component(
                        component_id=existing_component['id'],
                        component_data=component_data
                    )
                    
                    self.show_message("Success", f"Component '{existing_component['name']}' updated successfully!")
                    
                except Exception as e:
                    print(f"Error updating component: {e}")
                    self.show_message("Error", f"Failed to update component: {str(e)}")
                    
            else:
                # Show dialog for new component
                dialog = ctk.CTkToplevel(self)
                dialog.title("Save Component")
                self.center_dialog(dialog, width=400, height=200)
                
                # Create input frame
                input_frame = ctk.CTkFrame(dialog)
                input_frame.pack(fill="both", expand=True, padx=20, pady=20)
                
                # Component name input
                ctk.CTkLabel(
                    input_frame,
                    text="Component Name:",
                    anchor="w"
                ).pack(fill="x", pady=(0, 5))
                
                name_var = ctk.StringVar(value=f"New {data['type'].capitalize()}")
                name_entry = ctk.CTkEntry(
                    input_frame,
                    textvariable=name_var,
                    width=300
                )
                name_entry.pack(pady=(0, 15))
                
                def save_with_name():
                    name = name_var.get().strip()
                    if not name:
                        self.show_message("Error", "Component name is required")
                        return
                    
                    try:
                        # Import project_id from project_view
                        from views.project_view import project_id
                        
                        # Calculate actual dimensions based on unit and DPI
                        width_px = data['dimensions']['width']
                        height_px = data['dimensions']['height']
                        
                        if data['unit'] == 'mm':
                            # Convert mm to inches then to pixels
                            width_px = int((data['dimensions']['width'] / 25.4) * data['dpi'])
                            height_px = int((data['dimensions']['height'] / 25.4) * data['dpi'])
                        elif data['unit'] == 'cm':
                            # Convert cm to inches then to pixels
                            width_px = int((data['dimensions']['width'] / 2.54) * data['dpi'])
                            height_px = int((data['dimensions']['height'] / 2.54) * data['dpi'])
                        elif data['unit'] == 'in':
                            # Convert inches to pixels
                            width_px = int(data['dimensions']['width'] * data['dpi'])
                            height_px = int(data['dimensions']['height'] * data['dpi'])
                        
                        # Store all component data in properties
                        properties = {
                            'width': data['dimensions']['width'],
                            'height': data['dimensions']['height'],
                            'unit': data['unit'],
                            'dpi': data['dpi'],
                            'elements': self.element_manager.elements,
                            'background_color': self.canvas_manager.background_color,
                            'dimensions': {
                                'width': width_px,
                                'height': height_px,
                                'original_width': data['dimensions']['width'],
                                'original_height': data['dimensions']['height'],
                                'unit': data['unit']
                            }
                        }
                        
                        component_data = {
                            'name': name,
                            'type': data['type'],
                            'properties': properties
                        }
                        
                        # Create new component
                        self.component_controller.create_component(
                            project_id=project_id,
                            component_data=component_data
                        )
                        dialog.destroy()
                        self.show_message("Success", f"Component '{name}' saved successfully!")
                        
                    except Exception as e:
                        print(f"Error saving component: {e}")
                        self.show_message("Error", f"Failed to save component: {str(e)}")
                
                # Buttons frame
                button_frame = ctk.CTkFrame(input_frame)
                button_frame.pack(fill="x", pady=(0, 10))
                
                # Save button
                ctk.CTkButton(
                    button_frame,
                    text="Save",
                    command=save_with_name
                ).pack(side="left", padx=5)
                
                # Cancel button
                ctk.CTkButton(
                    button_frame,
                    text="Cancel",
                    command=dialog.destroy
                ).pack(side="right", padx=5)
                
        except Exception as e:
            print(f"Error showing save dialog: {e}")
            self.show_message("Error", f"Failed to show save dialog: {str(e)}")
    
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
    
    def _handle_undo(self, _):
        """Handle undo action"""
        state = self.history_manager.undo()
        if state is not None:
            self.element_manager.elements = state.elements.copy()
            self.canvas_manager.background_color = state.background_color
            self.canvas_manager.canvas.configure(bg=state.background_color)
            self.canvas_manager.render_elements(self.element_manager.elements)
            self.canvas_manager.clear_selection()
            self.selected_element = None
    
    def _handle_redo(self, _):
        """Handle redo action"""
        state = self.history_manager.redo()
        if state is not None:
            self.element_manager.elements = state.elements.copy()
            self.canvas_manager.background_color = state.background_color
            self.canvas_manager.canvas.configure(bg=state.background_color)
            self.canvas_manager.render_elements(self.element_manager.elements)
            self.canvas_manager.clear_selection()
            self.selected_element = None
    
    def _handle_element_edited(self, element):
        """Handle element editing"""
        # Push state to history after any element edit
        self.history_manager.push_state(
            self.element_manager.elements,
            self.canvas_manager.background_color
        )
        # Re-render the canvas
        self.canvas_manager.render_elements(self.element_manager.elements)
        if self.selected_element:
            self.canvas_manager.show_selection(self.selected_element)
    
    def _push_state(self):
        """Push current state to history"""
        self.history_manager.push_state(self.element_manager.elements) 
    
    def _handle_export_component(self, data):
        """Handle component export"""
        try:
            filename = data['filename']
            format = data['format']
            
            self.canvas_manager.clear_selection()
            self.canvas_manager.canvas.update()
            # Get base64 string from canvas
            base64_data = self._canvas_to_base64(self.canvas_manager.canvas)
            
            # Convert base64 to image and save
            self._save_base64_to_file(base64_data, filename, format)
            
            self.show_message("Success", f"Component exported successfully to {filename}")
            
        except Exception as e:
            print(f"Error exporting component: {e}")
            self.show_message("Error", f"Failed to export component: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _save_base64_to_file(self, base64_string: str, filename: str, format: str):
        """Convert base64 string to image file"""
        import base64
        from PIL import Image
        import io
        
        try:
            # Decode base64 string to bytes
            image_data = base64.b64decode(base64_string)
            
            # Create PIL Image from bytes
            image = Image.open(io.BytesIO(image_data))
            
            # Save in requested format
            image.save(filename, format)
            
        except Exception as e:
            print(f"Error saving base64 to file: {e}")
            raise
    
    def _canvas_to_base64(self, canvas):
        """Convert canvas content to base64 string"""
        import base64
        import io
        from PIL import Image, ImageGrab
        
        try:
            # Get canvas dimensions and position
            x = canvas.winfo_rootx()
            y = canvas.winfo_rooty()
            width = canvas.winfo_width()
            height = canvas.winfo_height()
            
            # Take a screenshot of the canvas area
            img = ImageGrab.grab(bbox=(x, y, x + width, y + height))
            
            # Save image to bytes buffer
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Convert to base64
            base64_string = base64.b64encode(buffer.getvalue()).decode()
            
            return base64_string
            
        except Exception as e:
            print(f"Error converting canvas to base64: {e}")
            # Try alternative method for macOS
            try:
                # Create a temporary PostScript file
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.ps', delete=False) as temp_file:
                    temp_ps = temp_file.name
                
                # Save canvas to PostScript
                canvas.postscript(
                    file=temp_ps,
                    colormode='color',
                    width=width,
                    height=height
                )
                
                # Convert PostScript to PIL Image
                img = Image.open(temp_ps)
                
                # Save to buffer and convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)
                
                # Clean up temp file
                import os
                os.unlink(temp_ps)
                
                # Convert to base64
                base64_string = base64.b64encode(buffer.getvalue()).decode()
                
                return base64_string
                
            except Exception as e2:
                print(f"Error with alternative method: {e2}")
                raise
    
    def load_component(self, component):
        """Load component data into editor"""
        try:
            # Clear current canvas and elements
            #self.canvas_manager.clear_canvas()
            self.element_manager.elements.clear()
            
            print(f"Loading component: {component}")  # Debug print
            
            # Load properties
            properties = json.loads(component['properties']) if isinstance(component['properties'], str) else component['properties']
            print(f"Parsed properties: {properties}")  # Debug print
            
            # Set canvas dimensions from properties
            width = properties.get('width', 800)
            height = properties.get('height', 600)
            unit = properties.get('unit', 'mm')
            dpi = properties.get('dpi', 96)
            self.current_component = component
            
            # Check for dimensions in nested structure
            # if 'dimensions' in properties:
            #     width = properties['dimensions'].get('width', width)
            #     height = properties['dimensions'].get('height', height)
            
            # Set canvas properties
            #self.canvas_manager.resize_canvas(width, height)
            
            # Set background color
            if 'background_color' in properties:
                bg_color = properties['background_color']
                self.canvas_manager.background_color = bg_color
                self.canvas_manager.canvas.configure(bg=bg_color)
            
            # Load elements
            if 'elements' in properties:
                for element in properties['elements']:
                    print(f"Loading element: {element}")  # Debug print
                    
                    # Add to element manager
                    self.element_manager.elements.append(element)
                    
                    # Draw element on canvas
                    self.canvas_manager._draw_element(element)
            
            # Update UI
            #self.update_ui()
            self.canvas_manager._handle_size_changed({
                'width': width,
                'height': height,
                'unit': unit,
                'dpi': dpi,
                'physical_width': width,
                'physical_height': height,
                'physical_unit': unit,
            })
            
            print("Component loaded successfully")  # Debug print
            
        except Exception as e:
            print(f"Error loading component: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to load component: {str(e)}")