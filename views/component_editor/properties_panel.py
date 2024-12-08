import customtkinter as ctk
from .events.event_types import EventType
from .events.event_manager import EventManager
from tkinter import filedialog
from utils.image_processor import ImageProcessor

class PropertiesPanel(ctk.CTkFrame):
    def __init__(self, parent, event_manager: EventManager):
        super().__init__(parent)
        self.event_manager = event_manager
        
        # Initialize variables with default card size (63x88mm)
        self.type_var = ctk.StringVar(value="card")
        self.width_var = ctk.StringVar(value="63")
        self.height_var = ctk.StringVar(value="88")
        self.unit_var = ctk.StringVar(value="mm")
        self.dpi_var = ctk.StringVar(value="96")  # Default DPI
        
        # Add trace to variables for live updates
        self.width_var.trace_add("write", self._update_canvas_size)
        self.height_var.trace_add("write", self._update_canvas_size)
        self.unit_var.trace_add("write", self._update_canvas_size)
        self.dpi_var.trace_add("write", self._update_canvas_size)
        
        # Configure frame properties
        self.configure(
            width=250,  # Fixed width in pixels
            height=600,  # Minimum height
            fg_color="black"  # Light background to distinguish the panel
        )
        
        # Prevent frame from shrinking below minimum size
        self.grid_propagate(False)
        self.pack_propagate(False)
        
        self._create_ui()
        # Initial canvas size update
        self._update_canvas_size()
    
    def _create_ui(self):
        """Create the properties panel UI"""
        # Component Type
        ctk.CTkLabel(self, text="Component Type:").pack(anchor="w", padx=5)
        self.type_menu = ctk.CTkOptionMenu(
            self,
            values=["card", "board"],
            variable=self.type_var,
            command=self._on_type_change
        )
        self.type_menu.pack(fill="x", padx=5, pady=(0, 10))
        
        # Dimensions Frame
        dims_frame = ctk.CTkFrame(self)
        dims_frame.pack(fill="x", padx=5, pady=(0, 10))
        
        # Width
        width_frame = ctk.CTkFrame(dims_frame)
        width_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(width_frame, text="Width:").pack(side="left", padx=5)
        width_entry = ctk.CTkEntry(width_frame, textvariable=self.width_var, width=50)
        width_entry.pack(side="left", padx=2)
        
        # Height
        height_frame = ctk.CTkFrame(dims_frame)
        height_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(height_frame, text="Height:").pack(side="left", padx=5)
        height_entry = ctk.CTkEntry(height_frame, textvariable=self.height_var, width=50)
        height_entry.pack(side="left", padx=2)
        
        # Unit Selection
        unit_frame = ctk.CTkFrame(dims_frame)
        unit_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(unit_frame, text="Unit:").pack(side="left", padx=5)
        unit_menu = ctk.CTkOptionMenu(
            unit_frame,
            values=["mm", "cm", "in", "px"],
            variable=self.unit_var,
            width=60
        )
        unit_menu.pack(side="left", padx=2)
        
        # DPI Selection
        dpi_frame = ctk.CTkFrame(dims_frame)
        dpi_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(dpi_frame, text="DPI:").pack(side="left", padx=5)
        dpi_menu = ctk.CTkOptionMenu(
            dpi_frame,
            values=["72", "96", "150", "300"],
            variable=self.dpi_var,
            width=60
        )
        dpi_menu.pack(side="left", padx=2)
        
        # Add separator
        separator = ctk.CTkFrame(self, height=1, fg_color="gray70")
        separator.pack(fill="x", padx=5, pady=10)
        
        # Canvas Background Section
        bg_frame = ctk.CTkFrame(self)
        bg_frame.pack(fill="x", padx=5, pady=(0, 10))
        
        ctk.CTkLabel(bg_frame, text="Canvas Background:").pack(anchor="w", padx=5, pady=(5,0))
        
        # Color preview and button frame
        color_frame = ctk.CTkFrame(bg_frame)
        color_frame.pack(fill="x", padx=5, pady=5)
        
        # Color preview
        self.color_preview = ctk.CTkCanvas(
            color_frame,
            width=30,
            height=30,
            highlightthickness=1,
            highlightbackground="gray70"
        )
        self.color_preview.pack(side="left", padx=5)
        
        # Initialize with white background
        self.current_bg_color = "#FFFFFF"
        self.color_preview.configure(bg=self.current_bg_color)
        
        # Color picker button
        self.color_btn = ctk.CTkButton(
            color_frame,
            text="Choose Color",
            command=self._choose_background_color,
            width=120
        )
        self.color_btn.pack(side="left", padx=5)
        
        # Button Frame for Save and Export
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(side="bottom", fill="x", padx=5, pady=5)
        
        # Save Button
        self.save_btn = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self._save_component
        )
        self.save_btn.pack(side="left", fill="x", expand=True, padx=(0, 2))
        
        # Export Button
        self.export_btn = ctk.CTkButton(
            button_frame,
            text="Export",
            command=self._export_component
        )
        self.export_btn.pack(side="right", fill="x", expand=True, padx=(2, 0))
    
    def _handle_template_action(self, action: str):
        """Handle template-related actions"""
        # Emit event for template action
        self.event_manager.emit(EventType.TEMPLATE_ACTION, action)
    
    def _on_type_change(self, new_type: str):
        """Handle component type change"""
        # Emit event for type change
        self.event_manager.emit(EventType.TYPE_CHANGED, new_type)
    
    def _update_canvas_size(self, *args):
        """Update canvas size when dimensions, units, or DPI change"""
        try:
            # Get current values
            width = float(self.width_var.get() or 0)
            height = float(self.height_var.get() or 0)
            unit = self.unit_var.get()
            dpi = int(self.dpi_var.get())
            
            # Skip if dimensions are 0
            if width <= 0 or height <= 0:
                return
                
            # Convert to pixels based on unit and DPI
            width_px = self._convert_to_pixels(width, unit)
            height_px = self._convert_to_pixels(height, unit)
            
            # Emit size change event with physical dimensions
            self.event_manager.emit(EventType.CANVAS_SIZE_CHANGED, {
                'width': width_px,
                'height': height_px,
                'width_unit': unit,
                'height_unit': unit,
                'original_width': width,
                'original_height': height,
                'dpi': dpi,
                'physical_width': width,  # Keep track of physical size
                'physical_height': height,
                'physical_unit': unit
            })
        except ValueError:
            # Handle invalid number input
            pass
    
    def _convert_to_pixels(self, value: float, unit: str) -> int:
        """Convert measurements to pixels based on unit and DPI"""
        try:
            dpi = int(self.dpi_var.get())
        except ValueError:
            dpi = 96  # Default to 96 DPI if invalid value
        
        # First convert everything to inches
        if unit == "mm":
            inches = value / 25.4  # 1 inch = 25.4 mm
        elif unit == "cm":
            inches = value / 2.54  # 1 inch = 2.54 cm
        elif unit == "in":
            inches = value
        else:  # px
            inches = value / dpi  # Convert pixels back to inches
        
        # Then convert inches to pixels using DPI
        return int(inches * dpi)
    
    def _save_component(self):
        """Save the current component"""
        # Emit event for saving component
        self.event_manager.emit(EventType.SAVE_COMPONENT, {
            'type': self.type_var.get(),
            'dimensions': {
                'width': int(self.width_var.get()),
                'height': int(self.height_var.get())
            },
            'unit': self.unit_var.get(),
            'dpi': int(self.dpi_var.get())
        })
    
    def _subscribe_to_events(self):
        """Subscribe to relevant events"""
        # Example: Subscribe to element selection to update properties
        self.event_manager.subscribe(
            EventType.ELEMENT_SELECTED,
            self._update_properties
        )
    
    def _update_properties(self, element):
        """Update properties based on selected element"""
        # Update UI based on element properties
        pass
    
    def _choose_background_color(self):
        """Open color picker dialog"""
        try:
            from tkinter import colorchooser
            color = colorchooser.askcolor(
                title="Choose Background Color",
                color=self.current_bg_color
            )
            
            if color[1]:  # color[1] is the hex value
                self.current_bg_color = color[1]
                self.color_preview.configure(bg=self.current_bg_color)
                
                # Emit event for canvas background change
                self.event_manager.emit(EventType.CANVAS_BACKGROUND_CHANGED, {
                    'color': self.current_bg_color
                })
        except Exception as e:
            print(f"Error choosing color: {e}")
    
    def _export_component(self):
        """Export the component as an image"""
        try:
        
            
            # Get current canvas dimensions
            width = float(self.width_var.get())
            height = float(self.height_var.get())
            unit = self.unit_var.get()
            dpi = int(self.dpi_var.get())
            
            # Create file dialog
            filetypes = [
                ('PNG files', '*.png'),
                ('JPEG files', '*.jpg'),
                ('All files', '*.*')
            ]
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=filetypes,
                title="Export Component"
            )
            
            if filename:
                # Get the file extension
                ext = filename.lower().split('.')[-1]
                
                # Create properties dictionary for image creation
                properties = {
                    'background_color': self.current_bg_color,
                    'width': self._convert_to_pixels(width, unit),
                    'height': self._convert_to_pixels(height, unit),
                    'dpi': dpi,
                    'unit': unit,
                    'physical_width': width,
                    'physical_height': height
                }
                
                # Emit event to request component export
                self.event_manager.emit(EventType.EXPORT_COMPONENT, {
                    'filename': filename,
                    'format': ext.upper(),
                    'properties': properties
                })
                
        except Exception as e:
            print(f"Error exporting component: {e}")
            import traceback
            traceback.print_exc()