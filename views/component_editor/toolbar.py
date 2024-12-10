import customtkinter as ctk
from PIL import Image
from typing import Dict, Callable
from .events.event_types import EventType
from .events.event_manager import EventManager

class Toolbar(ctk.CTkFrame):
    def __init__(self, parent, event_manager: EventManager):
        super().__init__(parent)
        self.event_manager = event_manager
        
        # Initialize tool variable
        self.tool_var = ctk.StringVar(value="select")
        self.tool_buttons: Dict = {}
        
        self._init_tools()
        self._subscribe_to_events()
    
    def _init_tools(self):
        """Initialize toolbar with tools"""
        tools = [
            ("select", "select_icon.png", "arrow", "Select (V)"),
            ("move", "move_icon.png", "fleur", "Move (M)"),
            ("resize", "resize_icon.png", "sizing", "Resize (R)"),
            ("text", "text_icon.png", "xterm", "Text"),
            ("shape", "shape_icon.png", "crosshair", "Shape"),
            ("image", "image_icon.png", "plus", "Image"),
            ("qrcode", "qrcode_icon.png", "plus", "QR Code")
        ]
        
        # Tool button styles
        button_width = 100
        button_height = 32
        icon_size = 24
        normal_color = "transparent"
        selected_color = "#3B8ED0"
        
        for tool_name, icon_file, cursor, label in tools:
            try:
                # Create frame to hold button
                tool_frame = ctk.CTkFrame(self, fg_color="transparent")
                tool_frame.pack(side="left", padx=2)
                
                # Load icon
                image_path = f"assets_static/icons/{icon_file}"
                pil_image = Image.open(image_path)
                icon_image = ctk.CTkImage(
                    light_image=pil_image,
                    dark_image=pil_image,
                    size=(icon_size, icon_size)
                )
                
                # Create button with icon and text
                btn = ctk.CTkButton(
                    tool_frame,
                    text=label,
                    image=icon_image,
                    width=button_width,
                    height=button_height,
                    fg_color=normal_color if self.tool_var.get() != tool_name else selected_color,
                    command=lambda t=tool_name: self._select_tool(t),
                    compound="left",
                )
                btn.pack()
                
                self.tool_buttons[tool_name] = {
                    "button": btn,
                    "cursor": cursor,
                    "normal_color": normal_color,
                    "selected_color": selected_color
                }
                
            except Exception as e:
                print(f"Error loading tool icon {icon_file}: {e}")
        
        # Add separator
        separator = ctk.CTkFrame(self, width=2, height=32)
        separator.pack(side="left", padx=10, pady=5)
        
        # Add Undo/Redo buttons
        self.undo_button = ctk.CTkButton(
            self,
            text="Undo",
            width=60,
            state="disabled",
            command=lambda: self.event_manager.emit(EventType.UNDO, None)
        )
        self.undo_button.pack(side="left", padx=2)
        
        self.redo_button = ctk.CTkButton(
            self,
            text="Redo",
            width=60,
            state="disabled",
            command=lambda: self.event_manager.emit(EventType.REDO, None)
        )
        self.redo_button.pack(side="left", padx=2)
        
        # Subscribe to state changes
        self.event_manager.subscribe(EventType.STATE_CHANGED, self._update_history_buttons)
    
    def _select_tool(self, tool_name: str):
        """Handle tool selection"""
        print(f"Selecting tool: {tool_name}")
        self.tool_var.set(tool_name)
        
        # Update button colors
        for name, tool_info in self.tool_buttons.items():
            tool_info["button"].configure(
                fg_color=tool_info["selected_color"] if name == tool_name else tool_info["normal_color"]
            )
        
        # Emit tool changed event
        self.event_manager.emit(EventType.TOOL_CHANGED, {
            'tool': tool_name,
            'cursor': self.tool_buttons[tool_name]["cursor"]
        })
    
    def _subscribe_to_events(self):
        """Subscribe to relevant events"""
        # Subscribe to element created event to auto-switch to select tool
        self.event_manager.subscribe(
            EventType.ELEMENT_CREATED,
            lambda _: self._select_tool('select')
        )
    
    def get_current_tool(self) -> str:
        """Get the currently selected tool"""
        return self.tool_var.get() 
    
    def _update_history_buttons(self, data):
        """Update undo/redo button states"""
        if data:
            self.undo_button.configure(state="normal" if data['can_undo'] else "disabled")
            self.redo_button.configure(state="normal" if data['can_redo'] else "disabled")