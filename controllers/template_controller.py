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


try:
    from views.component_editor.canvas_manager import CanvasManager
    from views.component_editor.element_manager import ElementManager
    from views.component_editor.events.event_manager import EventManager   
except ImportError:
    # Fallback imports if the component_editor module isn't in the expected location
    from ..views.component_editor.canvas_manager import CanvasManager
    from ..views.component_editor.element_manager import ElementManager
    from ..views.component_editor.events.event_manager import EventManager
import tempfile
import tkinter as tk

class TemplateController:
    def __init__(self, db_manager):
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
            data_path = os.path.join("./assets/data", csv_file)
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
                    'height': component.properties.get('height', 600)
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
    
    def export_template_image(self, template_data: dict, output_path: str ,temp_window=None) -> bool:
        """Export template as image using canvas rendering"""
        try:
            # Create temporary managers for rendering
            event_manager = EventManager()
            
            # Create a temporary top-level window for canvas
            #temp_window = preview_frame if preview_frame else ctk.CTkFrame()
            #temp_window.withdraw()  # Hide the window
            
            # Initialize managers with the temp window
            element_manager = ElementManager(event_manager, temp_window)
            
            # Initialize canvas manager
            canvas_manager = CanvasManager(temp_window, event_manager, element_manager)
            
            try:
                # Set canvas properties
                canvas_manager.background_color = template_data.get('background_color', '#FFFFFF')
                canvas_manager.canvas_width = template_data['dimensions']['width']
                canvas_manager.canvas_height = template_data['dimensions']['height']
                
                # Update canvas size
                # canvas_manager.canvas.configure(
                #     width=canvas_manager.canvas_width,
                #     height=canvas_manager.canvas_height,
                #     bg=canvas_manager.background_color
                # )
                
                print(f"Rendering elements {template_data['elements']}")
                # Render elements
                canvas = canvas_manager.render_elements_ondemand(template_data['elements'],exporting=True)
                canvas.update()  # Ensure all elements are rendered
                
                # Get canvas dimensions and position
                base64_data = self._canvas_to_base64(canvas)
            
                # Convert base64 to image and save
                self._save_base64_to_file(base64_data, output_path, 'PNG')
                return True
                
            finally:
                # Clean up
                temp_window.destroy()
                
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