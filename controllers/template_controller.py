import os
import json
from datetime import datetime
from models.template import Template
from models.template_manager import TemplateManager
from controllers.component_controller import ComponentController
from typing import Optional, List
import pandas as pd
from PIL import Image, ImageTk
import base64
import io
import customtkinter as ctk
from config import get_config

try:
    from views.component_editor.canvas_manager import CanvasManager
    from views.component_editor.element_manager import ElementManager
    from views.component_editor.events.event_manager import EventManager   
except ImportError:
    # Fallback imports if the component_editor module isn't in the expected location
    from ..views.component_editor.canvas_manager import CanvasManager
    from ..views.component_editor.element_manager import ElementManager
    from ..views.component_editor.events.event_manager import EventManager
import tkinter as tk

class TemplateController:
    def __init__(self, db_manager):
        self.config = get_config()  # Get config instance
        self.template_manager = TemplateManager(db_manager)
        self.component_controller = ComponentController(db_manager)
    def save_template(self, name: str, template_data: dict) -> bool:
        """Save a component template"""
        return self.template_manager.save_template(name, template_data)
    
    def load_template(self, name: str) -> dict:
        """Load a template by name"""
        return self.template_manager.load_template(name)
    
    def list_templates(self, category: str = None) -> list:
        """List all available templates"""
        return self.template_manager.list_templates(category)
    
    def delete_template(self, name: str) -> bool:
        """Delete a template"""
        return self.template_manager.delete_template(name)
    
    def update_template(self, name: str, template_data: dict) -> bool:
        """Update an existing template"""
        return self.template_manager.update_template(name, template_data)
     
    def get_all_templates(self) -> list:
        """Get all templates with their metadata"""
        templates = []
        template_names = self.template_manager.list_templates()
        
        for name in template_names:
            template_data = self.template_manager.load_template(name)
            if template_data and 'metadata' in template_data:
                # Create a template object with required attributes
                template = type('Template', (), {
                    'id': name,  # Use name as ID
                    'name': template_data['metadata']['name'],
                    'description': template_data.get('description', ''),
                    'updated_at': datetime.fromisoformat(template_data['metadata']['updated_at']),
                    'created_at': datetime.fromisoformat(template_data['metadata']['created_at'])
                })
                templates.append(template)
        
        return templates
    
    def create_template(self, name: str) -> bool:
        """Create a new empty template with sample elements"""
        template_data = {
            'type': 'card',  # Default type
            'dimensions': {
                'width': 63,
                'height': 88
            },
            'elements': [
                {
                    'type': 'text',
                    'id': 'title',
                    'x': 5,
                    'y': 5,
                    'width': 53,
                    'height': 10,
                    'text': 'Card Title',
                    'fontSize': 14,
                    'fontWeight': 'bold',
                    'align': 'center'
                },
                {
                    'type': 'image',
                    'id': 'artwork',
                    'x': 5,
                    'y': 20,
                    'width': 53,
                    'height': 40,
                    'src': '',
                    'preserveAspectRatio': True
                },
                {
                    'type': 'text',
                    'id': 'description',
                    'x': 5,
                    'y': 65,
                    'width': 53,
                    'height': 18,
                    'text': 'Card description goes here',
                    'fontSize': 10,
                    'multiline': True
                }
            ],
            'description': 'A basic card template',
            'category': 'cards'
        }
        return self.save_template(name, template_data)
    
    def edit_template(self, template_id: str, template_data: dict) -> bool:
        """Edit an existing template"""
        return self.update_template(template_id, template_data)
    
    def create_from_csv(self, template_name: str, csv_file: str, mappings: dict) -> bool:
        """Create components from CSV data source"""
        try:
            # Load template
            template = self.load_template(template_name)
            if not template:
                return False
            
            # Load CSV data
            data_path = self.config.USER_DATA_DIR / "data" / csv_file
            df = pd.read_csv(data_path)
            
            # Create components for each row
            components = []
            for _, row in df.iterrows():
                component_data = template.copy()
                
                # Apply mappings
                for csv_col, template_field in mappings.items():
                    # Find and update the element with matching field
                    for element in component_data['elements']:
                        if element.get('id') == template_field:
                            if element['type'] == 'text':
                                element['text'] = str(row[csv_col])
                            # Add other element type handling as needed
                
                components.append(component_data)
            
            return components
            
        except Exception as e:
            print(f"Error creating components from CSV: {e}")
            return False
    
    def create_from_component(self, component_id: str) -> bool:
        """Create a template from an existing component"""
        try:
            # Get component data from component controller
            component = self.component_controller.get_component_by_id(component_id)
            if not component:
                print(f"Component not found: {component_id}")
                return False
            
            # Create template name from component name
            template_name = f"Template_{component.name}"
            
            # Get elements and add unique IDs
            elements = component.properties.get('elements', [])
            for i, element in enumerate(elements):
                # Generate unique ID based on element type and index
                element_type = element.get('type', 'element')
                element['id'] = f"{element_type}_{i}"
            
            # Extract template data from component
            template_data = {
                'type': component.type,
                'dimensions': {
                    'width': component.properties.get('width', 800),
                    'height': component.properties.get('height', 600),
                    'unit': component.properties.get('unit', 'mm'),
                    'dpi': component.properties.get('dpi', 96),
                    'actual_width': component.properties.get('dimensions', {}).get('actual_width', 800),
                    'actual_height': component.properties.get('dimensions', {}).get('actual_height', 600)
                },
                'elements': elements,
                'description': f"Template created from component: {component.name}",
                'category': 'components',
                'metadata': {
                    'name': template_name,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat(),
                    'source_component': component_id
                }
            }
            
            # Save the template
            success = self.save_template(template_name, template_data)
            
            if success:
                print(f"Template created successfully: {template_name}")
            else:
                print(f"Failed to create template from component: {component_id}")
                
            return success
            
        except Exception as e:
            print(f"Error creating template from component: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def export_template_image(self, template_data: dict, output_path: str, preview_frame=None) -> bool:
        """Export template as image using canvas rendering"""
        try:
            # Create a dialog window for rendering
            dialog = ctk.CTkToplevel()
            dialog.title("Rendering...")
            
            # Get actual dimensions
            actual_width = template_data['dimensions'].get('actual_width', template_data['dimensions']['width'])
            actual_height = template_data['dimensions'].get('actual_height', template_data['dimensions']['height'])
            
            # Create a frame with fixed dimensions
            render_frame = ctk.CTkFrame(dialog, width=actual_width, height=actual_height)
            render_frame.pack_propagate(False)  # Prevent frame from shrinking
            render_frame.pack(padx=0, pady=0)
            
            # Create internal canvas for final rendering
            internal_canvas = tk.Canvas(
                render_frame,
                width=actual_width,
                height=actual_height,
                highlightthickness=0
            )
            internal_canvas.pack(expand=False, fill=None)
            
            # Initialize managers
            event_manager = EventManager()
            element_manager = ElementManager(event_manager, dialog)
            canvas_manager = CanvasManager(render_frame, event_manager, element_manager)
            
            # Configure canvas with explicit dimensions
            canvas = canvas_manager.canvas
            canvas.configure(width=actual_width, height=actual_height)
            canvas.pack(expand=False, fill=None)  # Don't allow canvas to resize
            
            # Force dialog update and geometry
            dialog.update_idletasks()
            dialog.geometry(f"{actual_width}x{actual_height}")
            
            try:
                # Render elements at actual size and get rendered canvas
                rendered_canvas = canvas_manager.render_elements_ondemand(template_data['elements'], exporting=True)
                
                # Copy rendered content to internal canvas
                internal_canvas.delete('all')
                for item in rendered_canvas.find_all():
                    # Get item type and coordinates
                    item_type = rendered_canvas.type(item)
                    coords = rendered_canvas.coords(item)
                    
                    # Copy item properties
                    config = {key: rendered_canvas.itemcget(item, key) 
                            for key in rendered_canvas.itemconfig(item)}
                    
                    # Create same item on internal canvas based on type
                    print("=== item_type", item_type)
                    try:
                        if item_type == "line":
                            if len(coords) >= 4:  # Ensure we have enough coordinates
                                internal_canvas.create_line(*coords, **config)
                        elif item_type == "text":
                            internal_canvas.create_text(*coords, **config)
                        elif item_type == "image":
                            internal_canvas.create_image(*coords, **config)
                        elif item_type == "rectangle":
                            internal_canvas.create_rectangle(*coords, **config)
                        # Add other types as needed
                    except Exception as e:
                        print(f"Error copying item type {item_type}: {e}")
                        continue
                
                # Multiple update cycles to ensure complete rendering
                for _ in range(3):
                    internal_canvas.update_idletasks()
                    dialog.update_idletasks()
                    dialog.update()
                
                # Additional wait for rendering
                dialog.after(1000)
                
                # Get base64 string from internal canvas
                base64_data = self._canvas_to_base64(internal_canvas)
                
                # Save to file
                self._save_base64_to_file(base64_data, output_path, 'PNG')
                
                # Update preview if provided
                if preview_frame:
                    for widget in preview_frame.winfo_children():
                        widget.destroy()
                    
                    # Load and verify the saved image
                    from PIL import Image, ImageTk
                    preview_img = Image.open(output_path)
                    
                    # Verify image dimensions
                    if preview_img.size == (1, 1):
                        raise Exception("Generated image is 1x1 pixel - rendering failed")
                    
                    # Calculate scaling to fit preview frame
                    preview_width = preview_frame.winfo_width()
                    preview_height = preview_frame.winfo_height()
                    
                    width_scale = preview_width / actual_width
                    height_scale = preview_height / actual_height
                    print("=== width_scale", width_scale)
                    print("=== height_scale", height_scale)
                    print("=== actual_width", actual_width)
                    print("=== actual_height", actual_height)
                    scale = min(width_scale, height_scale)
                    print("=== scale", scale)
                    # Resize preview image
                    preview_size = (int(actual_width * scale), int(actual_height * scale))
                    print("=== preview_size", preview_size)
                    preview_img = preview_img.resize(preview_size, Image.Resampling.LANCZOS)
                    
                    # Create and display preview
                    preview_photo = ImageTk.PhotoImage(preview_img)
                    preview_label = tk.Label(preview_frame, image=preview_photo)
                    preview_label.image = preview_photo  # Keep a reference
                    preview_label.pack(expand=True)
                
                return True
                
            finally:
                # Clean up
                dialog.destroy()  # Commented out to keep dialog visible
                
        except Exception as e:
            print(f"Error exporting template image: {e}")
            import traceback
            traceback.print_exc()
            return False
    def _canvas_to_base64(self, canvas):
        """Convert canvas content to base64 string"""
        import base64
        import io
        from PIL import Image, ImageGrab
        
        try:
            # Ensure canvas is fully updated
            canvas.update_idletasks()
            canvas.update()
            
            # Wait a bit for rendering
            canvas.after(100)
            
            # Get the absolute coordinates of the canvas on screen
            x = canvas.winfo_rootx()
            y = canvas.winfo_rooty()
            width = canvas.winfo_width()
            height = canvas.winfo_height()
            
            # Take a screenshot of the exact canvas area
            # Add a small offset to account for any borders
            img = ImageGrab.grab(
                bbox=(
                    x ,  # Add small offset to avoid border
                    y ,  # Add small offset to avoid border
                    x + width,
                    y + height
                ),
                include_layered_windows=True  # This helps with some rendering issues
            )
            
            # Save image to bytes buffer
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Convert to base64
            base64_string = base64.b64encode(buffer.getvalue()).decode()
            
            return base64_string
            
        except Exception as e:
            print(f"Error converting canvas to base64: {e}")
            raise
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