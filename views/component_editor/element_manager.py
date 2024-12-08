from typing import Dict, Any, Optional, List
from .events.event_types import EventType
from .events.event_manager import EventManager
import customtkinter as ctk
from ..dialogs.text_dialog import TextDialog
from ..dialogs.shape_dialog import ShapeDialog
from ..dialogs.image_dialog import ImageDialog
from ..dialogs.qrcode_dialog import QRCodeDialog

class ElementManager:
    def __init__(self, event_manager: EventManager, parent_window: ctk.CTk, asset_controller=None):
        self.event_manager = event_manager
        self.parent_window = parent_window
        self.asset_controller = asset_controller
        self.elements: List[Dict[str, Any]] = []
        self.selected_element = None
        
    def create_element(self, element_type: str, x: int, y: int) -> Dict[str, Any]:
        """Create a new element with default properties"""
        new_element = {
            'type': element_type,
            'x': x,
            'y': y,
            'properties': self._get_default_properties(element_type)
        }
        
        self.elements.append(new_element)
        self.event_manager.emit(EventType.ELEMENT_CREATED, new_element)
        self.parent_window.after(100, lambda: self.event_manager.emit(EventType.STATE_CHANGED, None))
        return new_element
    
    def find_element_at(self, x: int, y: int) -> Optional[Dict[str, Any]]:
        """Find element at the given coordinates"""
        for element in reversed(self.elements):  # Check from top to bottom
            if self._is_point_inside_element(x, y, element):
                return element
        return None
    
    def _is_point_inside_element(self, x: int, y: int, element: Dict[str, Any]) -> bool:
        """Check if a point is inside an element"""
        element_x = element.get('x', 0)
        element_y = element.get('y', 0)
        width = element.get('properties', {}).get('width', 100)
        height = element.get('properties', {}).get('height', 100)
        
        return (element_x <= x <= element_x + width and 
                element_y <= y <= element_y + height)
    
    def move_element(self, element: Dict[str, Any], new_x: int, new_y: int) -> None:
        """Move an element to new coordinates"""
        if element in self.elements:
            element['x'] = new_x
            element['y'] = new_y
            self.event_manager.emit(EventType.ELEMENT_MOVED, element)
    
    def resize_element(self, element: Dict[str, Any], new_width: int, new_height: int) -> None:
        """Resize an element"""
        if element in self.elements:
            element['properties']['width'] = new_width
            element['properties']['height'] = new_height
            self.event_manager.emit(EventType.ELEMENT_RESIZED, element)
    
    def delete_element(self, element: Dict[str, Any]) -> None:
        """Delete an element"""
        if element in self.elements:
            self.elements.remove(element)
            self.event_manager.emit(EventType.ELEMENT_DELETED, element)
            self.parent_window.after(100, lambda: self.event_manager.emit(EventType.STATE_CHANGED, None))
    
    def _get_default_properties(self, element_type: str) -> Dict[str, Any]:
        """Get default properties for element type"""
        if element_type == 'text':
            return {
                'text': 'New Text',
                'font': 'Arial',
                'fontSize': 12,
                'fill': 'black',
                'bold': False,
                'italic': False,
                'align': 'left',
                'width': 200,
                'height': 100,
                'isTextBox': True
            }
        elif element_type == 'shape':
            return {
                'width': 100,
                'height': 100,
                'fill': 'white',
                'outline': 'black',
                'opacity': 1.0
            }
        elif element_type == 'image':
            return {
                'width': 100,
                'height': 100,
                'image_path': ''
            }
        elif element_type == 'qrcode':
            return {
                'width': 120,
                'height': 120,
                'content': 'https://tomobit.com',
                'fill': 'black',
                'background': None
            }
        return {}
    
    def edit_text_element(self, element: Dict[str, Any]) -> None:
        """Open text element edit dialog"""
        try:
            def on_save(properties: Dict[str, Any]):
                # Update element properties
                if 'properties' not in element:
                    element['properties'] = {}
                element['properties'].update(properties)
                self.event_manager.emit(EventType.ELEMENT_EDITED, element)

            # Create and show dialog
            TextDialog(
                parent=self.parent_window,
                element=element,
                on_save=on_save
            )
            
        except Exception as e:
            print(f"Error editing element: {e}")
    
    def edit_shape_element(self, element: Dict[str, Any]) -> None:
        """Open shape element edit dialog"""
        try:
            def on_save(properties: Dict[str, Any]):
                # Update element properties
                if 'properties' not in element:
                    element['properties'] = {}
                element['properties'].update(properties)
                self.event_manager.emit(EventType.ELEMENT_EDITED, element)

            # Create and show dialog
            ShapeDialog(
                parent=self.parent_window,
                element=element,
                on_save=on_save
            )
            
        except Exception as e:
            print(f"Error editing shape element: {e}")
    
    def edit_image_element(self, element: Dict[str, Any]) -> None:
        """Open image element edit dialog"""
        try:
            def on_save(properties: Dict[str, Any]):
                # Update element properties
                if 'properties' not in element:
                    element['properties'] = {}
                element['properties'].update(properties)
                print(f"Updated image properties: {properties}")  # Debug log
                self.event_manager.emit(EventType.ELEMENT_EDITED, element)

            # Create and show dialog
            ImageDialog(
                parent=self.parent_window,
                element=element,
                asset_controller=self.asset_controller,
                on_save=on_save
            )
            
        except Exception as e:
            print(f"Error editing image element: {e}")
    
    def edit_qrcode_element(self, element: Dict[str, Any]) -> None:
        """Open QR code edit dialog"""
        try:
            def on_save(properties: Dict[str, Any]):
                # Create new element if it's not in the elements list
                is_new = element not in self.elements
                
                # Update element properties
                if 'properties' not in element:
                    element['properties'] = {}
                element['properties'].update(properties)
                
                # Add element if it's new
                # if is_new:
                #     self.elements.append(element)
                #     self.event_manager.emit(EventType.ELEMENT_CREATED, element)
                # else:
                self.event_manager.emit(EventType.ELEMENT_EDITED, element)
                
                # Update canvas
                #self.event_manager.emit(EventType.STATE_CHANGED, None)

            # Create and show dialog
            QRCodeDialog(
                parent=self.parent_window,
                on_save=on_save
            )
            
        except Exception as e:
            print(f"Error editing QR code element: {e}")
            import traceback
            traceback.print_exc()
    
    def _get_parent_window(self) -> Optional[ctk.CTk]:
        """Get the parent window for dialogs"""
        return self.parent_window
    
    def select_element(self, element: Dict[str, Any]) -> None:
        """Select an element"""
        self.selected_element = element
        self.event_manager.emit(EventType.ELEMENT_SELECTED, element)