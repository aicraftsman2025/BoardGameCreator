import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from .events.event_types import EventType
from .events.event_manager import EventManager
import qrcode

class CanvasManager:
    def __init__(self, parent, event_manager: EventManager, element_manager):
        print("Initializing CanvasManager...")  # Debug
        
        # Initialize managers
        self.event_manager = event_manager
        self.element_manager = element_manager
        
        # Create main frame with pack
        self.canvas_frame = tk.Frame(parent, bg='gray90')
        self.canvas_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add background color attribute with default value
        self.background_color = "#FFFFFF"  # Default to white
        
        # Initialize states
        self.selected_element = None
        self.dragging = False
        self.move_start = None
        self.selection_items = []
        self.element_ids = {}
        self.image_refs = {}
        self.next_image_ref_id = 1
        
        # Initialize size tracking with default values
        self.canvas_width = 300  # Default width in pixels
        self.canvas_height = 300  # Default height in pixels
        self.current_unit = 'px'
        self.current_dpi = 96
        
        # Create canvas
        self._create_canvas()
        
        # Subscribe to events
        self._subscribe_to_events()
        print("Event subscriptions completed")  # Debug
    
    def get_frame(self):
        """Return the main frame of the canvas manager"""
        return self.canvas_frame
    
    def _create_canvas(self):
        """Create canvas without scrollbars"""
        # Create canvas with a border
        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg=self.background_color,
            highlightthickness=1,
            highlightbackground="gray70",
            width=self.canvas_width,
            height=self.canvas_height
        )
        
        # Center the canvas in its frame
        self.canvas.pack(expand=True)
        
        # Bind events
        self._bind_canvas_events()
        
        return self.canvas
    
    def _bind_canvas_events(self):
        """Bind all canvas events"""
        self.canvas.tag_bind("selectable", "<Button-1>", self._on_element_click)
        self.canvas.tag_bind("selectable", "<Double-Button-1>", self._on_element_double_click)
        self.canvas.tag_bind("handle", "<Button-1>", self._on_handle_click)
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release)
        self.canvas.bind("<Button-3>", self._show_context_menu)
        self.canvas.bind("<Key>", self._handle_key)
        
        # Add zoom bindings
        self.canvas.bind("<Control-MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Control-Button-4>", self._on_mousewheel)
        self.canvas.bind("<Control-Button-5>", self._on_mousewheel)

        
        # Make canvas focusable
        self.canvas.config(takefocus=1)
    
    def _on_element_click(self, event):
        """Handle element click"""
        clicked_id = self.canvas.find_closest(event.x, event.y)[0]
        if clicked_id in self.element_ids:
            element = self.element_ids[clicked_id]
            self.selected_element = element
            self.show_selection(element)
            
            # Emit selection event
            self.event_manager.emit(EventType.ELEMENT_SELECTED, element)
            
            # Start potential drag operation
            self.dragging = True
            self.move_start = (event.x, event.y)
            
            return "break"  # Prevent event propagation
    
    def _get_element_bounds(self, element):
        """Get element bounds with safe property access"""
        properties = element.get('properties', {})
        
        # Default sizes if not specified
        width = properties.get('width', 100)  # Default width
        height = properties.get('height', 100)  # Default height
        
        # For text elements, might need to get actual bounds
        if element.get('type') == 'text':
            # Get text bounds if available
            text_id = None
            for item_id, elem in self.element_ids.items():
                if elem == element:
                    text_id = item_id
                    break
            
            if text_id:
                bbox = self.canvas.bbox(text_id)
                if bbox:
                    width = bbox[2] - bbox[0]
                    height = bbox[3] - bbox[1]
        
        return {
            'x': element.get('x', 0),
            'y': element.get('y', 0),
            'width': width,
            'height': height
        }
    
    def _find_exact_element_at(self, x, y):
        """Find element exactly at the given coordinates"""
        items = self.canvas.find_overlapping(x-1, y-1, x+1, y+1)
        element_items = [item for item in items if "element" in self.canvas.gettags(item)]
        
        if not element_items:
            return None
            
        # Get exact coordinates of each element
        for item_id in reversed(element_items):  # Check from top to bottom
            if item_id not in self.element_ids:
                continue
                
            element = self.element_ids[item_id]
            bounds = self._get_element_bounds(element)
            
            # Check if point is inside element's bounds
            if (bounds['x'] <= x <= bounds['x'] + bounds['width'] and 
                bounds['y'] <= y <= bounds['y'] + bounds['height']):
                return element
        
        return None
    
    def _on_canvas_click(self, event):
        """Handle canvas click events"""
        if not hasattr(self, 'current_tool'):
            self.current_tool = 'select'
        
        print(f"Current tool: {self.current_tool}")

        # Find exact element at click position
        clicked_element = self._find_exact_element_at(event.x, event.y)
        print(f"Clicked element: {clicked_element}")
        if clicked_element:
            # Select the element
            self.selected_element = clicked_element
            
            if self.current_tool == 'move':
                # Enable dragging only for move tool
                self.dragging = True
                self.move_start = (event.x - clicked_element['x'], event.y - clicked_element['y'])
            elif self.current_tool == 'resize':
                # Start resize operation
                self.resize_start = (event.x, event.y)
                self.original_size = {
                    'width': clicked_element.get('properties', {}).get('width', 100),
                    'height': clicked_element.get('properties', {}).get('height', 100)
                }
                # Change cursor to resize (using correct cursor name)
                try:
                    self.canvas.configure(cursor="sizing")  # Primary choice
                except tk.TclError:
                    try:
                        self.canvas.configure(cursor="bottom_right_corner")  # Alternative
                    except tk.TclError:
                        self.canvas.configure(cursor="arrow")  # Fallback
            
            self.show_selection(clicked_element)
            self.event_manager.emit(EventType.CANVAS_CLICKED, {
                'x': event.x,
                'y': event.y,
                'element': clicked_element
            })
            return "break"
        
        # If clicked on empty space, deselect
        self.selected_element = None
        self.clear_selection()
        self.event_manager.emit(EventType.CANVAS_CLICKED, {
            'x': event.x,
            'y': event.y,
            'element': None
        })
    
    def _on_canvas_drag(self, event):
        """Handle canvas drag events"""
        if not self.selected_element:
            return
        
        if self.dragging and self.move_start and self.current_tool == 'move':
            # Change cursor to move cursor
            self.canvas.configure(cursor="fleur")
            
            # Calculate new position
            dx = event.x - self.move_start[0]
            dy = event.y - self.move_start[1]
            
            # Update element position
            self.selected_element['x'] = dx
            self.selected_element['y'] = dy
            
            # Re-render and show selection
            self.render_elements(self.element_manager.elements)
            self.show_selection(self.selected_element)
            
            # Emit drag event
            self.event_manager.emit(EventType.CANVAS_DRAGGED, {
                'element': self.selected_element,
                'x': event.x,
                'y': event.y
            })
        elif self.current_tool == 'resize' and self.selected_element:
            if not hasattr(self, 'resize_start'):
                # Start resize if not already started
                self.resize_start = (event.x, event.y)
                self.original_size = {
                    'width': self.selected_element.get('properties', {}).get('width', 100),
                    'height': self.selected_element.get('properties', {}).get('height', 100)
                }
            
            # Calculate new dimensions
            dx = event.x - self.resize_start[0]
            dy = event.y - self.resize_start[1]
            
            new_width = max(20, self.original_size['width'] + dx)
            new_height = max(20, self.original_size['height'] + dy)
            
            # Convert pixels to current unit for display
            display_width = self._convert_from_pixels(new_width, self.current_unit, self.current_dpi)
            display_height = self._convert_from_pixels(new_height, self.current_unit, self.current_dpi)
            
            # Update element properties
            if 'properties' not in self.selected_element:
                self.selected_element['properties'] = {}
            
            self.selected_element['properties']['width'] = new_width
            self.selected_element['properties']['height'] = new_height
            
            # Show size label - clear existing first
            self.canvas.delete("size_label_bg")
            self.canvas.delete("size_label_text")
            self._show_size_label(display_width, display_height, event.x, event.y)
            
            # Re-render elements
            self.render_elements(self.element_manager.elements)
            self.show_selection(self.selected_element)
            
            print(f"Resizing to: {display_width:.1f} × {display_height:.1f} {self.current_unit}")  # Debug
    
    def _on_canvas_release(self, event):
        """Handle mouse release events"""
        if self.selected_element:
            if self.dragging or self.resize_state.get('active'):
                self.event_manager.emit(EventType.ELEMENT_EDITED, {
                    'element': self.selected_element
                })
        
        # Remove size labels if they exist
        if hasattr(self, 'size_label_bg'):
            self.canvas.delete(self.size_label_bg)
            delattr(self, 'size_label_bg')
        if hasattr(self, 'size_label'):
            self.canvas.delete(self.size_label)
            delattr(self, 'size_label')
        
        # Reset states
        self.dragging = False
        self.move_start = None
        self.resize_state = {'active': False}
        self.original_position = None
        
        # Reset cursor
        self.canvas.configure(cursor="arrow")
    
    def _subscribe_to_events(self):
        """Subscribe to relevant events"""
        print("Subscribing to events...")  # Debug
        
        self.event_manager.subscribe(
            EventType.TOOL_CHANGED,
            self._handle_tool_changed
        )
        print(f"Subscribed to TOOL_CHANGED event")  # Debug
        
        self.event_manager.subscribe(
            EventType.ELEMENT_DESELECTED,
            lambda _: self.clear_selection()
        )
        
        # Add new subscriptions for properties panel events
        self.event_manager.subscribe(
            EventType.CANVAS_SIZE_CHANGED,
            self._handle_size_changed
        )
        
        self.event_manager.subscribe(
            EventType.CANVAS_BACKGROUND_CHANGED,
            self._handle_background_changed
        )
        
        self.event_manager.subscribe(
            EventType.ELEMENT_CREATED,
            lambda _: self.render_elements(self.element_manager.elements)
        )
        
        self.event_manager.subscribe(
            EventType.ELEMENT_EDITED,
            lambda _: self.render_elements(self.element_manager.elements)
        )
    
    def _handle_tool_changed(self, data):
        """Handle tool change events"""
        if data:
            self.current_tool = data.get('tool', 'select')
            cursor = data.get('cursor', 'arrow')
            self.canvas.configure(cursor=cursor)
            print(f"Tool changed to: {self.current_tool}")
            print(f"Data: {data}")
    
    def _handle_background_changed(self, data):
        """Handle canvas background color change"""
        if data and 'color' in data:
            self.background_color = data['color']
            self.canvas.configure(bg=self.background_color)
            print(f"Canvas background color updated to: {self.background_color}")
    
    def _handle_size_changed(self, data):
        """Handle canvas size change event"""
        if not data:
            return
        
        try:
            # Get physical dimensions and DPI from the event data
            physical_width = float(data.get('physical_width', 0))
            physical_height = float(data.get('physical_height', 0))
            physical_unit = data.get('physical_unit', 'px')
            dpi = float(data.get('dpi', 96))
            
            # Convert physical dimensions to pixels
            if physical_unit == 'mm':
                width_px = int((physical_width / 25.4) * dpi)
                height_px = int((physical_height / 25.4) * dpi)
            elif physical_unit == 'cm':
                width_px = int((physical_width / 2.54) * dpi)
                height_px = int((physical_height / 2.54) * dpi)
            elif physical_unit == 'in':
                width_px = int(physical_width * dpi)
                height_px = int(physical_height * dpi)
            else:  # 'px'
                width_px = int(physical_width)
                height_px = int(physical_height)
            
            # Ensure minimum size
            width_px = max(width_px, 1)
            height_px = max(height_px, 1)
            
            # Update internal dimensions
            self.canvas_width = width_px
            self.canvas_height = height_px
            self.current_unit = physical_unit
            self.current_dpi = dpi
            
            # Configure canvas with actual pixel dimensions
            self.canvas.configure(
                width=width_px,
                height=height_px
            )
            
            # Force canvas to resize
            self.canvas.update()
            
            # Re-render elements if they exist
            if hasattr(self, 'element_manager') and self.element_manager:
                self.render_elements(self.element_manager.elements)
                
            print(f"Physical size: {physical_width}{physical_unit} x {physical_height}{physical_unit}")
            print(f"Actual pixels: {width_px}px x {height_px}px")
            print(f"DPI: {dpi}")
            print(f"Canvas size updated to: {self.canvas.winfo_width()}x{self.canvas.winfo_height()}")
            
        except Exception as e:
            print(f"Error updating canvas size: {e}")
            import traceback
            traceback.print_exc()
    
    def _convert_to_pixels(self, value, unit, dpi):
        """Convert a value from any unit to pixels"""
        try:
            value = float(value)
            # Convert to inches first
            if unit == 'mm':
                inches = value / 25.4  # 1 inch = 25.4 mm
            elif unit == 'cm':
                inches = value / 2.54  # 1 inch = 2.54 cm
            elif unit == 'in':
                inches = value
            else:  # 'px' or default
                return int(value)
            
            # Convert inches to pixels using DPI
            return int(inches * dpi)
        except ValueError:
            print(f"Error converting {value}{unit} to pixels")
            return 0
    
    def _convert_from_pixels(self, pixels, unit, dpi):
        """Convert pixels to specified unit"""
        try:
            pixels = float(pixels)
            # Convert pixels to inches
            inches = pixels / dpi
            
            # Convert inches to target unit
            if unit == 'mm':
                return inches * 25.4  # 1 inch = 25.4 mm
            elif unit == 'cm':
                return inches * 2.54  # 1 inch = 2.54 cm
            elif unit == 'in':
                return inches
            else:  # 'px' or default
                return pixels
        except ValueError:
            print(f"Error converting {pixels}px to {unit}")
            return 0
    
    def _update_canvas_pixels(self, width_pixels, height_pixels):
        """Update canvas size using pixel values"""
        try:
            # Ensure minimum dimensions
            width_pixels = max(1, int(width_pixels))
            height_pixels = max(1, int(height_pixels))
            
            # Update canvas size
            self.canvas.configure(width=width_pixels)
            self.canvas.configure(height=height_pixels)
            
            # Update scroll region
            self.canvas.configure(scrollregion=(0, 0, width_pixels, height_pixels))
            
            # Force update
            self.canvas.update_idletasks()
            
            # Re-render elements
            if hasattr(self, 'element_manager') and self.element_manager:
                self.render_elements(self.element_manager.elements)
            
            print(f"Canvas updated to: {width_pixels}x{height_pixels} pixels")
            print(f"Actual canvas size: {self.canvas.winfo_width()}x{self.canvas.winfo_height()}")
            
        except Exception as e:
            print(f"Error updating canvas pixels: {e}")
            import traceback
            traceback.print_exc()
    
    def get_canvas_size(self, unit=None):
        """Get current canvas size in specified unit"""
        if unit is None:
            unit = self.current_unit
        
        width = self._convert_from_pixels(self.canvas_width, unit, self.current_dpi)
        height = self._convert_from_pixels(self.canvas_height, unit, self.current_dpi)
        
        return {
            'width': width,
            'height': height,
            'unit': unit,
            'dpi': self.current_dpi
        }
    
    def update_canvas_properties(self, width, height, unit, dpi):
        """Public method to update canvas properties from property panel"""
        try:
            print(f"Updating canvas properties: {width}{unit} x {height}{unit} at {dpi} DPI")
            
            # Convert all inputs to appropriate types
            width = float(width)
            height = float(height)
            dpi = float(dpi)
            
            # Validate inputs
            if width <= 0 or height <= 0 or dpi <= 0:
                print("Invalid dimensions or DPI")
                return
            
            # Update canvas size
            self._handle_size_changed({
                'width': width,
                'height': height,
                'unit': unit,
                'dpi': dpi
            })
            
        except Exception as e:
            print(f"Error updating canvas properties: {e}")
            import traceback
            traceback.print_exc()
    
    def render_elements(self, elements):
        """Render all elements on the canvas"""
        # Store current size label if it exists
        size_label_info = None
        if hasattr(self, 'size_label') and hasattr(self, 'size_label_bg'):
            size_label_info = {
                'bg': self.size_label_bg,
                'text': self.size_label
            }
        
        self.canvas.delete("element")  # Clear existing elements
        self.canvas.delete("element_base")  # Also clear base elements
        self.element_ids.clear()
        self.image_refs.clear()
        self.next_image_ref_id = 1
        print(f"Rendering {(elements)} elements")
        for element in elements:
            self._draw_element(element)
        
        # Reshow selection if there's a selected element
        if self.selected_element:
            self.show_selection(self.selected_element)
        
        # Restore size label if it existed
        if size_label_info:
            self.canvas.lift(size_label_info['text'])
            self.canvas.lift(size_label_info['bg'])
    
    def _draw_element(self, element, canvas=None):
        """Draw a single element on the canvas"""
        # Use provided canvas or default to self.canvas
        target_canvas = canvas or self.canvas
        
        element_type = element.get('type')
        properties = element.get('properties', {})
        x = element.get('x', 0)
        y = element.get('y', 0)
        width = properties.get('width', 100)
        height = properties.get('height', 100)
        
        canvas_id = None
        
        if element_type == 'text':
            text = properties.get('text', 'New Text')
            font_name = properties.get('font', 'Arial')
            font_size = properties.get('fontSize', 12)
            fill = properties.get('fill', 'black')
            bold = properties.get('bold', False)
            italic = properties.get('italic', False)
            align = properties.get('align', 'left')
            
            font_style = []
            if bold: font_style.append('bold')
            if italic: font_style.append('italic')
            font_style = ' '.join(font_style) if font_style else 'normal'
            
            # Create text with width constraint for wrapping
            canvas_id = target_canvas.create_text(
                x, y,
                text=text,
                font=(font_name, font_size, font_style),
                fill=fill,
                anchor="nw",
                justify=align,
                width=width,
                tags=("element", "selectable")
            )
        
        elif element_type == 'shape':
            # Get shape properties
            fill = properties.get('fill', 'white')
            outline = properties.get('outline', 'black')
            radius = int(properties.get('radius', 0))
            opacity = float(properties.get('opacity', 1.0))
            outline_width = int(properties.get('outline_width', 1))
            border_style = properties.get('dash', 'Solid')
            
            # Create PIL image with transparency
            img = Image.new('RGBA', (int(width), int(height)), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Convert colors to RGBA
            fill_rgba = self._hex_to_rgba(fill, opacity)
            outline_rgba = self._hex_to_rgba(outline, 1.0)  # Border always solid
            
            # Draw shape on PIL image
            if radius > 0:
                # Rounded rectangle
                draw.rounded_rectangle(
                    [0, 0, width-1, height-1],
                    radius=radius,
                    fill=fill_rgba,
                    outline=outline_rgba,
                    width=outline_width
                )
            else:
                # Regular rectangle
                draw.rectangle(
                    [0, 0, width-1, height-1],
                    fill=fill_rgba,
                    outline=outline_rgba,
                    width=outline_width
                )
            
            # Handle border style
            if border_style != 'Solid':
                # Create a separate image for the border
                border_img = Image.new('RGBA', (int(width), int(height)), (0, 0, 0, 0))
                border_draw = ImageDraw.Draw(border_img)
                
                # Draw dashed border
                dash_pattern = self._get_dash_pattern(border_style, outline_width)
                if dash_pattern:
                    self._draw_dashed_border(
                        border_draw,
                        [0, 0, width-1, height-1],
                        radius,
                        outline_rgba,
                        outline_width,
                        dash_pattern
                    )
                
                # Composite the border onto the main image
                img = Image.alpha_composite(img, border_img)
            
            # Convert to PhotoImage
            photo_image = ImageTk.PhotoImage(img)
            
            # Store reference to prevent garbage collection
            ref_id = f"shape_{self.next_image_ref_id}"
            self.next_image_ref_id += 1
            self.image_refs[ref_id] = photo_image
            
            # Create canvas image
            canvas_id = target_canvas.create_image(
                x, y,
                image=photo_image,
                anchor="nw",
                tags=("element", "selectable")
            )
        
        elif element_type == 'image':
            # Image handling remains the same
            image_path = properties.get('path')
            if image_path:
                try:
                    pil_image = Image.open(image_path)
                    pil_image = pil_image.resize((int(width), int(height)), Image.Resampling.LANCZOS)
                    photo_image = ImageTk.PhotoImage(pil_image)
                    
                    ref_id = f"img_{self.next_image_ref_id}"
                    self.next_image_ref_id += 1
                    self.image_refs[ref_id] = photo_image
                    
                    canvas_id = target_canvas.create_image(
                        x, y,
                        image=photo_image,
                        anchor="nw",
                        tags=("element", "selectable")
                    )
                except Exception as e:
                    print(f"Error loading image {image_path}: {e}")
                    canvas_id = target_canvas.create_rectangle(
                        x, y,
                        x + width,
                        y + height,
                        fill='lightgray',
                        outline='gray',
                        tags=("element", "selectable")
                    )
        elif element_type == 'qrcode':
            try:
                print("Rendering QR code")
                # Get element properties
                x = element.get('x', 0)
                y = element.get('y', 0)
                properties = element.get('properties', {})
                width = properties.get('width', 200)
                height = properties.get('height', 200)
                content = properties.get('content', '')
                
                # Generate QR code
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(content)
                qr.make(fit=True)
                
                # Create QR code image
                qr_image = qr.make_image(fill_color="black", back_color="white")
                
                # Resize image to match element dimensions
                qr_image = qr_image.resize((width, height), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo_image = ImageTk.PhotoImage(qr_image)
                
                # Store reference to prevent garbage collection
                image_ref_id = self.next_image_ref_id
                self.image_refs[image_ref_id] = photo_image
                self.next_image_ref_id += 1
                
                # Create canvas image
                item_id = target_canvas.create_image(
                    x + width/2,  # Center the image
                    y + height/2,
                    image=photo_image,
                    tags=("element", "selectable", "qrcode")
                )
                
                # Store element reference
                self.element_ids[item_id] = element
                
                # Add selection handles if selected
                if element == self.selected_element:
                    self.show_selection(element)
                    
            except Exception as e:
                print(f"Error rendering QR code: {e}")
                import traceback
                traceback.print_exc()
        
        if canvas_id:
            self.element_ids[canvas_id] = element
        
        return canvas_id
    
    def _hex_to_rgba(self, color, opacity):
        """Convert color (hex or name) to RGBA tuple"""
        # Color name mapping to hex
        COLOR_MAP = {
            'white': '#FFFFFF',
            'black': '#000000',
            'red': '#FF0000',
            'green': '#00FF00',
            'blue': '#0000FF',
            'yellow': '#FFFF00',
            'purple': '#800080',
            'orange': '#FFA500',
            'gray': '#808080',
            'lightgray': '#D3D3D3',
            'darkgray': '#A9A9A9',
            'transparent': '#FFFFFF'
        }
        
        # If color is a name, convert to hex
        if color.lower() in COLOR_MAP:
            color = COLOR_MAP[color.lower()]
        
        # Remove '#' if present
        hex_color = color.lstrip('#')
        
        try:
            # Convert hex to RGB
            r = int(hex_color[:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
        except (ValueError, IndexError):
            # Fallback to white if invalid color
            print(f"Invalid color: {color}, falling back to white")
            r, g, b = 255, 255, 255
        
        # Add alpha channel
        a = int(opacity * 255)
        
        return (r, g, b, a)
    
    def show_selection(self, element):
        """Show selection border and resize handles around the element"""
        self.clear_selection()
        
        if not element:
            return
        
        # Get element bounds
        bounds = self._get_element_bounds(element)
        x = bounds['x']
        y = bounds['y']
        width = bounds['width']
        height = bounds['height']
        
        # Draw selection border
        border = self.canvas.create_rectangle(
            x - 2, y - 2,
            x + width + 2, y + height + 2,
            outline="blue",
            width=2,
            tags="selection"
        )
        self.selection_items.append(border)
        
        # Draw resize handles
        handle_size = 6
        handles = [
            (x - handle_size, y - handle_size),                    # Top-left
            (x + width/2 - handle_size/2, y - handle_size),        # Top-middle
            (x + width, y - handle_size),                          # Top-right
            (x - handle_size, y + height/2 - handle_size/2),       # Middle-left
            (x + width, y + height/2 - handle_size/2),             # Middle-right
            (x - handle_size, y + height),                         # Bottom-left
            (x + width/2 - handle_size/2, y + height),            # Bottom-middle
            (x + width, y + height)                               # Bottom-right
        ]
        
        for hx, hy in handles:
            handle = self.canvas.create_rectangle(
                hx, hy,
                hx + handle_size, hy + handle_size,
                fill="white",
                outline="blue",
                tags=("handle", "selection")
            )
            self.selection_items.append(handle)
        
        # Ensure selection stays above elements but below size label
        for item in self.selection_items:
            self.canvas.tag_raise(item)
        if hasattr(self, 'size_label'):
            self.canvas.tag_raise(self.size_label)
        if hasattr(self, 'size_label_bg'):
            self.canvas.tag_raise(self.size_label_bg)
    
    def clear_selection(self):
        """Clear all selection visuals"""
        for item in self.selection_items:
            self.canvas.delete(item)
        self.selection_items.clear()
    
    def _on_element_double_click(self, event):
        """Handle double click on elements"""
        clicked_id = self.canvas.find_closest(event.x, event.y)[0]
        if clicked_id in self.element_ids:
            element = self.element_ids[clicked_id]
            
            # Create save callback
            def on_save(properties):
                if 'properties' not in element:
                    element['properties'] = {}
                element['properties'].update(properties)
                self.render_elements(self.element_manager.elements)
                self.show_selection(element)
                self.event_manager.emit(EventType.ELEMENT_EDITED, {
                    'element': element
                })
            
            # Open appropriate dialog based on element type
            if element['type'] == 'text':
                from views.dialogs.text_dialog import TextDialog
                dialog = TextDialog(self.canvas, element, on_save)
            elif element['type'] == 'shape':
                from views.dialogs.shape_dialog import ShapeDialog
                dialog = ShapeDialog(self.canvas, element, on_save)
            elif element['type'] == 'image':
                from views.dialogs.image_dialog import ImageDialog
                dialog = ImageDialog(self.canvas, element, on_save)
            elif element['type'] == 'qrcode':
                from views.dialogs.qrcode_dialog import QRCodeDialog
                dialog = QRCodeDialog(self.canvas, element, on_save)
            
            # Select the element
            self.selected_element = element
            self.show_selection(element)
            
            # Emit selection event
            self.event_manager.emit(EventType.ELEMENT_SELECTED, {
                'element': element
            })
            
            return "break"  # Prevent event propagation
    
    def _on_handle_click(self, event):
        """Handle clicks on resize handles"""
        if not self.selected_element:
            return
        
        # Get handle position
        handle_id = self.canvas.find_closest(event.x, event.y)[0]
        handle_tags = self.canvas.gettags(handle_id)
        
        # Store original size and position for resize operation
        self.resize_start = (event.x, event.y)
        self.original_size = {
            'width': self.selected_element.get('properties', {}).get('width', 100),
            'height': self.selected_element.get('properties', {}).get('height', 100)
        }
        self.original_position = {
            'x': self.selected_element.get('x', 0),
            'y': self.selected_element.get('y', 0)
        }
        
        # Set appropriate cursor based on handle position
        try:
            self.canvas.configure(cursor="sizing")
        except tk.TclError:
            try:
                self.canvas.configure(cursor="bottom_right_corner")
            except tk.TclError:
                self.canvas.configure(cursor="arrow")
        
        return "break"  # Prevent event propagation
    
    def _edit_selected(self):
        """Edit the selected element from context menu"""
        if self.selected_element:
            self._edit_element(self.selected_element)
    
    def _on_handle_click(self, event):
        """Handle clicks on resize handles"""
        if not self.selected_element:
            return
        
        # Store original size for resize operation
        self.resize_start = (event.x, event.y)
        self.original_size = {
            'width': self.selected_element.get('properties', {}).get('width', 100),
            'height': self.selected_element.get('properties', {}).get('height', 100)
        }
        
        # Change cursor to resize
        self.canvas.configure(cursor="se-resize")
        
        # Stop event propagation
        return "break"
    
    def _start_resize(self, event, handle_position='SE'):
        """Start resize operation"""
        if not self.selected_element:
            return False
            
        bounds = self._get_element_bounds(self.selected_element)
        
        self.resize_state = {
            'active': True,
            'handle': handle_position,
            'start_x': event.x,
            'start_y': event.y,
            'original_width': bounds['width'],
            'original_height': bounds['height'],
            'original_x': bounds['x'],
            'original_y': bounds['y']
        }
        
        # Show initial size label
        display_width = self._convert_from_pixels(bounds['width'], self.current_unit, self.current_dpi)
        display_height = self._convert_from_pixels(bounds['height'], self.current_unit, self.current_dpi)
        self._show_size_label(display_width, display_height, event.x, event.y)
        
        return True
    
    def _handle_resize(self, event):
        """Handle resize operation"""
        if not self.resize_state['active'] or not self.selected_element:
            return
            
        # Calculate deltas
        dx = event.x - self.resize_state['start_x']
        dy = event.y - self.resize_state['start_y']
        
        # Get original values
        orig_width = self.resize_state['original_width']
        orig_height = self.resize_state['original_height']
        orig_x = self.resize_state['original_x']
        orig_y = self.resize_state['original_y']
        
        # Initialize new values
        new_width = orig_width
        new_height = orig_height
        new_x = orig_x
        new_y = orig_y
        
        # Update based on handle position
        handle = self.resize_state['handle']
        
        if handle in ['NW', 'SW']:  # Left handles
            new_width = max(20, orig_width - dx)
            new_x = orig_x + (orig_width - new_width)
        if handle in ['NE', 'SE']:  # Right handles
            new_width = max(20, orig_width + dx)
        
        # For text elements, only allow width resizing
        if self.selected_element['type'] == 'text':
            # Update width for text wrapping
            if 'properties' not in self.selected_element:
                self.selected_element['properties'] = {}
            self.selected_element['properties']['width'] = new_width
            
            # Position updates
            self.selected_element['x'] = new_x
            self.selected_element['y'] = new_y
            
            # Re-render to get new wrapped height
            self.render_elements(self.element_manager.elements)
            
            # Get actual height after wrapping
            for item_id, elem in self.element_ids.items():
                if elem == self.selected_element:
                    bbox = self.canvas.bbox(item_id)
                    if bbox:
                        new_height = bbox[3] - bbox[1]
                        self.selected_element['properties']['height'] = new_height
                    break
        else:
            # Normal resize for non-text elements
            if handle in ['NW', 'NE']:  # Top handles
                new_height = max(20, orig_height - dy)
                new_y = orig_y + (orig_height - new_height)
            if handle in ['SW', 'SE']:  # Bottom handles
                new_height = max(20, orig_height + dy)
            
            # Update element properties
            if 'properties' not in self.selected_element:
                self.selected_element['properties'] = {}
            
            self.selected_element['x'] = new_x
            self.selected_element['y'] = new_y
            self.selected_element['properties']['width'] = new_width
            self.selected_element['properties']['height'] = new_height
        
        # Convert to current unit for display
        display_width = self._convert_from_pixels(new_width, self.current_unit, self.current_dpi)
        display_height = self._convert_from_pixels(new_height, self.current_unit, self.current_dpi)
        
        # Show size label with current dimensions
        self._show_size_label(display_width, display_height, event.x, event.y)
        
        # Re-render elements
        self.render_elements(self.element_manager.elements)
        self.show_selection(self.selected_element)
    
    def _show_size_label(self, width, height, x, y):
        """Show size label with current dimensions"""
        # Format size text with current unit
        size_text = f"{width:.1f} × {height:.1f} {self.current_unit}"
        
        # Create background for better visibility
        # self.size_label_bg = self.canvas.create_rectangle(
        #     x + 10, y - 25,
        #     x + 150, y - 5,
        #     fill="#333333",  # Dark gray background
        #     stipple="gray50",  # Creates a semi-transparent effect
        #     tags="size_label_bg"
        # )
        
        # Create text label
        self.size_label = self.canvas.create_text(
            x + 15, y - 15,
            text=size_text,
            fill="blue",
            anchor="w",
            tags="size_label_text"
        )
        
        print(f"Size label created: {size_text}")  # Debug
    
    def _show_context_menu(self, event):
        """Show context menu for canvas or selected element"""
        # Create context menu
        context_menu = tk.Menu(self.canvas, tearoff=0)
        
        if self.selected_element:
            # Menu items for selected element
            context_menu.add_command(
                label="Delete",
                command=lambda: self._delete_selected_element()
            )
            context_menu.add_command(
                label="Duplicate",
                command=lambda: self._duplicate_selected_element()
            )
            context_menu.add_separator()
            context_menu.add_command(
                label="Bring to Front",
                command=lambda: self._bring_to_front()
            )
            context_menu.add_command(
                label="Send to Back",
                command=lambda: self._send_to_back()
            )
        else:
            # Menu items for canvas
            context_menu.add_command(
                label="Paste",
                command=lambda: self._paste_element()
            )
            context_menu.add_command(
                label="Select All",
                command=lambda: self._select_all()
            )
        
        # Show context menu at mouse position
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def _delete_selected_element(self):
        """Delete the selected element"""
        if self.selected_element:
            # Find and remove the element from the element manager's list
            elements = self.element_manager.elements
            if self.selected_element in elements:
                elements.remove(self.selected_element)
                
                # Clear selection
                self.selected_element = None
                self.clear_selection()
                
                # Re-render canvas
                self.render_elements(elements)
                
                # Emit event
                self.event_manager.emit(EventType.ELEMENT_DELETED, None)
                print("Element deleted")

    def _duplicate_selected_element(self):
        """Duplicate the selected element"""
        if self.selected_element:
            # Create a deep copy of the element
            import copy
            new_element = copy.deepcopy(self.selected_element)
            
            # Offset the position slightly
            new_element['x'] += 20
            new_element['y'] += 20
            
            # Add to element manager's list
            self.element_manager.elements.append(new_element)
            
            # Select the new element
            self.selected_element = new_element
            
            # Re-render canvas
            self.render_elements(self.element_manager.elements)
            self.show_selection(new_element)
            
            # Emit event
            self.event_manager.emit(EventType.ELEMENT_CREATED, new_element)
            print("Element duplicated")

    def _bring_to_front(self):
        """Bring selected element to front"""
        if self.selected_element:
            elements = self.element_manager.elements
            if self.selected_element in elements:
                # Remove and append to end (top)
                elements.remove(self.selected_element)
                elements.append(self.selected_element)
                
                # Re-render canvas
                self.render_elements(elements)
                self.show_selection(self.selected_element)
                print("Element brought to front")

    def _send_to_back(self):
        """Send selected element to back"""
        if self.selected_element:
            elements = self.element_manager.elements
            if self.selected_element in elements:
                # Remove and insert at beginning (bottom)
                elements.remove(self.selected_element)
                elements.insert(0, self.selected_element)
                
                # Re-render canvas
                self.render_elements(elements)
                self.show_selection(self.selected_element)
                print("Element sent to back")

    def _paste_element(self):
        """Paste element from clipboard"""
        if hasattr(self, 'clipboard') and self.clipboard:
            # Create a deep copy of the clipboard content
            import copy
            new_element = copy.deepcopy(self.clipboard)
            
            # Offset the position
            new_element['x'] += 20
            new_element['y'] += 20
            
            # Add to element manager's list
            self.element_manager.elements.append(new_element)
            
            # Select the new element
            self.selected_element = new_element
            
            # Re-render canvas
            self.render_elements(self.element_manager.elements)
            self.show_selection(new_element)
            
            # Emit event
            self.event_manager.emit(EventType.ELEMENT_CREATED, new_element)
            print("Element pasted")

    def _select_all(self):
        """Select all elements"""
        # For now, just select the last element if any exist
        if self.element_manager.elements:
            self.selected_element = self.element_manager.elements[-1]
            self.show_selection(self.selected_element)
            print("Last element selected")
    
    def _get_dash_pattern(self, style, width):
        """Convert border style to dash pattern"""
        # Scale dash patterns based on line width
        scale = max(1, width)
        
        patterns = {
            'Solid': None,  # No dash pattern
            'Dash': (4 * scale, 2 * scale),  # Long dashes
            'Dot': (2 * scale, 2 * scale),   # Dots
            'Dash Dot': (4 * scale, 2 * scale, 2 * scale, 2 * scale),  # Dash-dot pattern
            'Dash Dot Dot': (4 * scale, 2 * scale, 2 * scale, 2 * scale, 2 * scale, 2 * scale)  # Dash-dot-dot pattern
        }
        
        return patterns.get(style, None)  # Default to solid if style not found
    
    def _draw_dashed_border(self, draw, bbox, radius, color, width, dash_pattern):
        """Draw dashed border using line segments"""
        x1, y1, x2, y2 = bbox
        
        # Draw lines with dash pattern
        if radius > 0:
            # Draw lines for rounded rectangle
            draw.line([(x1 + radius, y1), (x2 - radius, y1)], fill=color, width=width, dash=dash_pattern)  # Top
            draw.line([(x2, y1 + radius), (x2, y2 - radius)], fill=color, width=width, dash=dash_pattern)  # Right
            draw.line([(x2 - radius, y2), (x1 + radius, y2)], fill=color, width=width, dash=dash_pattern)  # Bottom
            draw.line([(x1, y2 - radius), (x1, y1 + radius)], fill=color, width=width, dash=dash_pattern)  # Left
        else:
            # Draw lines for regular rectangle
            draw.line([(x1, y1), (x2, y1)], fill=color, width=width, dash=dash_pattern)  # Top
            draw.line([(x2, y1), (x2, y2)], fill=color, width=width, dash=dash_pattern)  # Right
            draw.line([(x2, y2), (x1, y2)], fill=color, width=width, dash=dash_pattern)  # Bottom
            draw.line([(x1, y2), (x1, y1)], fill=color, width=width, dash=dash_pattern)  # Left
    
    def _update_canvas_size(self, width: int, height: int):
        """Legacy method for compatibility"""
        self._handle_size_changed({
            'width': width,
            'height': height,
            'unit': 'px',  # Force pixels for legacy method
            'dpi': self.current_dpi or 96
        })
    
    def add_element(self, element_type, x=None, y=None, properties=None):
        """Add a new element to the canvas"""
        try:
            # Default to center if no position specified
            if x is None:
                x = self.canvas_width / 2
            if y is None:
                y = self.canvas_height / 2
            
            # Create element with default properties
            element = {
                'type': element_type,
                'x': x,
                'y': y,
                'properties': properties or {}
            }
            
            # Add element through element manager
            if self.element_manager:
                self.element_manager.add_element(element)
                
                # Render the new element
                self.render_elements(self.element_manager.elements)
                
                # Select the new element
                self.selected_element = element
                self.show_selection(element)
                
            print(f"Added new {element_type} element at ({x}, {y})")
            
        except Exception as e:
            print(f"Error adding element: {e}")
            import traceback
            traceback.print_exc()
    
    def update_background_color(self, color):
        """Update canvas background color"""
        try:
            self.background_color = color
            self.canvas.configure(bg=color)
            print(f"Updated canvas background color to: {color}")
        except Exception as e:
            print(f"Error updating background color: {e}")
    
    def _handle_key(self, event):
        """Handle keyboard events"""
        if not self.selected_element:
            return
        
        # Handle delete key
        if event.keysym in ('Delete', 'BackSpace'):
            self._delete_selected_element()
        
        # Handle copy/paste
        elif event.state & 4 and event.keysym == 'c':  # Ctrl+C
            self._copy_selected_element()
        elif event.state & 4 and event.keysym == 'v':  # Ctrl+V
            self._paste_element()
        
        # Handle arrow keys for fine movement
        elif event.keysym in ('Left', 'Right', 'Up', 'Down'):
            dx = 1 if event.keysym == 'Right' else (-1 if event.keysym == 'Left' else 0)
            dy = 1 if event.keysym == 'Down' else (-1 if event.keysym == 'Up' else 0)
            
            # Move element
            self.selected_element['x'] += dx
            self.selected_element['y'] += dy
            
            # Re-render and show selection
            self.render_elements(self.element_manager.elements)
            self.show_selection(self.selected_element)
            
            # Emit event
            self.event_manager.emit(EventType.ELEMENT_EDITED, {
                'element': self.selected_element
            })
    
    def _copy_selected_element(self):
        """Copy selected element to clipboard"""
        if self.selected_element:
            import json
            import copy
            
            # Create a deep copy of the element
            clipboard_data = copy.deepcopy(self.selected_element)
            
            # Store in class variable (simple clipboard implementation)
            self.clipboard = clipboard_data
            
            print("Element copied to clipboard")
    
    def _on_mousewheel(self, event):
        """Handle zoom with mousewheel"""
        # Determine zoom direction
        if event.delta > 0 or event.num == 4:
            self.scale_factor *= 1.1  # Zoom in
        else:
            self.scale_factor *= 0.9  # Zoom out
        
        # Limit scale factor
        self.scale_factor = max(0.1, min(2.0, self.scale_factor))
        
        # Update canvas size
        self._update_canvas_scale()
    
    def _update_canvas_scale(self):
        """Update canvas size based on scale factor"""
        display_width = int(self.canvas_width * self.scale_factor)
        display_height = int(self.canvas_height * self.scale_factor)
        
        self.canvas.configure(
            width=display_width,
            height=display_height
        )
        self._center_canvas()
    
    def _center_canvas(self):
        """Center the canvas content"""
        # Get the canvas and window dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        window_width = self.canvas_frame.winfo_width()
        window_height = self.canvas_frame.winfo_height()
        
        # Calculate scroll positions to center content
        x_pos = (self.canvas_width - window_width) / 2 if self.canvas_width > window_width else 0
        y_pos = (self.canvas_height - window_height) / 2 if self.canvas_height > window_height else 0
        
        # Update scroll position
        self.canvas.xview_moveto(x_pos / self.canvas_width if self.canvas_width > 0 else 0)
        self.canvas.yview_moveto(y_pos / self.canvas_height if self.canvas_height > 0 else 0)
    
    def add_qrcode(self, x=None, y=None):
        """Add a new QR code element to the canvas"""
        try:
            # Default to center if no position specified
            if x is None:
                x = self.canvas_width / 2
            if y is None:
                y = self.canvas_height / 2
            
            # Create QR code element with default properties
            element = {
                'type': 'qrcode',
                'x': x,
                'y': y,
                'properties': {
                    'width': 200,
                    'height': 200,
                    'content': 'Sample QR Code'
                }
            }
            
            print(f"Creating new QR code element at ({x}, {y})")
            
            # Add element through element manager
            if self.element_manager:
                self.element_manager.add_element(element)
                
                # Render the new element
                self.render_elements(self.element_manager.elements)
                
                # Select the new element
                self.selected_element = element
                self.show_selection(element)
                
                print("QR code element added successfully")
                
        except Exception as e:
            print(f"Error adding QR code: {e}")
            import traceback
            traceback.print_exc()
    
    def render_elements_ondemand(self, elements, exporting=False):
        """Render elements and return canvas for external use"""
        try:
            print(f"Rendering {len(elements)} elements")  # Debug
            
            # Clear existing elements
            self.canvas.delete("all")
            
            # Store element references
            self.element_ids = {}
            self.next_image_ref_id = 0
            self.image_refs = {}
            
            # Draw background
            self.canvas.configure(bg=self.background_color)
            
            # Calculate canvas dimensions based on elements
            max_x = max_y = 0
            for element in elements:
                x = element.get('x', 0)
                y = element.get('y', 0)
                properties = element.get('properties', {})
                width = properties.get('width', 100)
                height = properties.get('height', 100)
                max_x = max(max_x, x + width)
                max_y = max(max_y, y + height)
            
            # Update canvas size with padding
            padding = 40  # Increased padding for labels
            self.canvas_width = max_x + padding
            self.canvas_height = max_y + padding
            
            self.canvas.configure(
                width=self.canvas_width,
                height=self.canvas_height
            )
            
            # Draw each element
            for element in elements:
                try:
                    # Draw element with its ID as a tag
                    element_id = element.get('id', '')
                    print(f"Drawing element {element_id}")  # Debug
                    
                    # Store element reference
                    canvas_item = self._draw_element(element)
                    if canvas_item:
                        self.element_ids[canvas_item] = element
                
                except Exception as e:
                    print(f"Error drawing element: {e}")

            # Add ID labels after drawing all elements to ensure they're on top
            if not exporting:
                for element in elements:
                    try:
                        element_id = element.get('id', '')
                        bounds = self._get_element_bounds(element)
                        label_y = max(10, bounds['y'] - 15)  # Ensure y position is not negative
                        label_x = max(10, bounds['x'])
                        label = self.canvas.create_text(
                            label_x,
                            label_y,  # Use adjusted y position
                            text=f"ID: {element_id}",
                            fill="red",
                            anchor="w",
                            tags=f"id_label_{element_id}"
                        )
                        print(f"Created label for element {element_id}")  # Debug
                    except Exception as e:
                        print(f"Error creating label: {e}")
            
            # Update canvas
            self.canvas.update()
            print("Canvas updated successfully")  # Debug
            
            return self.canvas
            
        except Exception as e:
            print(f"Error in render_elements_ondemand: {e}")
            import traceback
            traceback.print_exc()