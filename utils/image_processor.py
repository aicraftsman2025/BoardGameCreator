from PIL import Image, ImageDraw, ImageFont
import os
from typing import Tuple, Dict
import io

class ImageProcessor:
    def __init__(self, fonts_dir="assets/fonts"):
        self.fonts_dir = fonts_dir
        self._load_default_fonts()
    
    def _load_default_fonts(self):
        """Load default fonts"""
        self.default_font = ImageFont.load_default()
        try:
            # Try to load a better default font if available
            font_path = os.path.join(self.fonts_dir, "Arial.ttf")
            if os.path.exists(font_path):
                self.default_font = ImageFont.truetype(font_path, 12)
        except Exception:
            pass
    
    def create_component_image(self, properties: Dict, elements: list) -> Image:
        """Create a new component image with all elements"""
        # Create base image
        width = properties.get('width', 300)
        height = properties.get('height', 300)
        
        # Create image with transparent background
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Set background color if specified
        if bg_color := properties.get('background_color'):
            bg_color = self._convert_color(bg_color)
            draw.rectangle([0, 0, width, height], fill=bg_color)
        
        # Sort elements by z-index (if available)
        sorted_elements = sorted(elements, key=lambda e: e.get('properties', {}).get('z_index', 0))
        
        # Draw all elements
        for element in sorted_elements:
            self._draw_element(img, draw, element)
        
        return img
    
    def _draw_element(self, img: Image, draw: ImageDraw, element: Dict):
        """Draw a single element on the image"""
        element_type = element.get('type')
        properties = element.get('properties', {})
        x = element.get('x', 0)
        y = element.get('y', 0)
        width = properties.get('width', 100)
        height = properties.get('height', 100)
        
        if element_type == 'text':
            # Get text properties with exact same keys as canvas
            text = properties.get('text', 'New Text')
            font_name = properties.get('font', 'Arial')
            font_size = properties.get('fontSize', 12)
            fill = properties.get('fill', 'black')
            bold = properties.get('bold', False)
            italic = properties.get('italic', False)
            align = properties.get('align', 'left')
            
            # Construct font style string
            font_style = []
            if bold: font_style.append('Bold')
            if italic: font_style.append('Italic')
            font_filename = f"{font_name}{' '.join(font_style)}.ttf" if font_style else f"{font_name}.ttf"
            
            try:
                font = ImageFont.truetype(
                    os.path.join(self.fonts_dir, font_filename),
                    font_size
                )
            except Exception as e:
                print(f"Font error: {e}, using default font")
                font = self.default_font
            
            # Calculate text wrapping and positioning
            lines = []
            current_line = []
            words = text.split()
            
            for word in words:
                current_line.append(word)
                test_line = ' '.join(current_line)
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] > width and len(current_line) > 1:
                    lines.append(' '.join(current_line[:-1]))
                    current_line = [word]
            lines.append(' '.join(current_line))
            
            # Calculate total text height
            line_height = font.getsize('hg')[1] * 1.2  # 1.2 for line spacing
            total_height = line_height * len(lines)
            
            # Draw each line with proper alignment
            for i, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                
                # Calculate x position based on alignment
                if align == 'center':
                    line_x = x + (width - line_width) / 2
                elif align == 'right':
                    line_x = x + width - line_width
                else:  # left
                    line_x = x
                
                # Draw the line
                draw.text(
                    (line_x, y + i * line_height),
                    line,
                    font=font,
                    fill=fill
                )
        
        elif element_type == 'shape':
            # Get shape properties
            fill = properties.get('fill', 'white')
            outline = properties.get('outline', 'black')
            radius = int(properties.get('radius', 0))
            opacity = float(properties.get('opacity', 1.0))
            outline_width = int(properties.get('outline_width', 1))
            border_style = properties.get('dash', 'Solid')
            
            # Convert colors to RGBA
            fill_rgba = self._hex_to_rgba(fill, opacity)
            outline_rgba = self._hex_to_rgba(outline, 1.0)
            
            if radius > 0:
                # Draw rounded rectangle
                self._draw_rounded_rectangle(
                    draw,
                    [x, y, x + width - 1, y + height - 1],
                    radius,
                    fill_rgba,
                    outline_rgba,
                    outline_width,
                    border_style
                )
            else:
                # Draw regular rectangle
                draw.rectangle(
                    [x, y, x + width - 1, y + height - 1],
                    fill=fill_rgba,
                    outline=outline_rgba,
                    width=outline_width
                )
        
        elif element_type == 'image':
            # Draw image
            try:
                with Image.open(properties.get('path', '')) as element_img:
                    width = properties.get('width', element_img.width)
                    height = properties.get('height', element_img.height)
                    element_img = element_img.resize((width, height))
                    img.paste(element_img, (x, y))
            except Exception as e:
                print(f"Error drawing image element: {e}")
        
        elif element_type == 'qrcode':
            # Draw QR code
            try:
                import qrcode
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(properties.get('content', ''))
                qr.make(fit=True)
                qr_img = qr.make_image(fill_color="black", back_color="white")
                
                width = properties.get('width', 200)
                height = properties.get('height', 200)
                qr_img = qr_img.resize((width, height))
                
                # Convert to RGBA if necessary
                if qr_img.mode != 'RGBA':
                    qr_img = qr_img.convert('RGBA')
                
                img.paste(qr_img, (x, y))
            except Exception as e:
                print(f"Error drawing QR code: {e}")
    
    def resize_image(self, img: Image, size: Tuple[int, int]) -> Image:
        """Resize image maintaining aspect ratio"""
        return img.resize(size, Image.Resampling.LANCZOS)
    
    def crop_image(self, img: Image, box: Tuple[int, int, int, int]) -> Image:
        """Crop image to specified box"""
        return img.crop(box)
    
    def save_image(self, img: Image, output_path: str, format: str = 'PNG'):
        """Save image to file"""
        img.save(output_path, format)
        return output_path
    
    def _convert_color(self, color: str) -> str:
        """Convert color to PIL-compatible format"""
        if not color:
            return None
        
        # Handle transparent color
        if color.lower() == 'transparent':
            return None
        
        # Handle hex colors
        if color.startswith('#'):
            return color
        
        # Handle named colors
        try:
            from PIL import ImageColor
            return ImageColor.getrgb(color)
        except:
            return color
    
    def _hex_to_rgba(self, hex_color: str, opacity: float = 1.0):
        """Convert hex color to RGBA tuple"""
        if not hex_color:
            return None
        
        try:
            # Remove '#' if present
            hex_color = hex_color.lstrip('#')
            
            # Convert hex to RGB
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            # Add alpha channel
            rgba = rgb + (int(opacity * 255),)
            return rgba
        except Exception as e:
            print(f"Error converting color {hex_color}: {e}")
            return None
    
    def _draw_rounded_rectangle(self, draw, coords, radius, fill, outline, width, border_style):
        """Draw a rounded rectangle"""
        x1, y1, x2, y2 = coords
        diameter = radius * 2
        
        # Draw the main shape
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
        
        # Draw the corners
        draw.ellipse([x1, y1, x1 + diameter, y1 + diameter], fill=fill)
        draw.ellipse([x2 - diameter, y1, x2, y1 + diameter], fill=fill)
        draw.ellipse([x1, y2 - diameter, x1 + diameter, y2], fill=fill)
        draw.ellipse([x2 - diameter, y2 - diameter, x2, y2], fill=fill)
        
        # Draw the outline if specified
        if outline and width > 0:
            if border_style == 'Solid':
                # Draw solid outline
                draw.arc([x1, y1, x1 + diameter, y1 + diameter], 180, 270, outline, width)
                draw.arc([x2 - diameter, y1, x2, y1 + diameter], 270, 0, outline, width)
                draw.arc([x1, y2 - diameter, x1 + diameter, y2], 90, 180, outline, width)
                draw.arc([x2 - diameter, y2 - diameter, x2, y2], 0, 90, outline, width)
                draw.line([x1 + radius, y1, x2 - radius, y1], outline, width)
                draw.line([x1 + radius, y2, x2 - radius, y2], outline, width)
                draw.line([x1, y1 + radius, x1, y2 - radius], outline, width)
                draw.line([x2, y1 + radius, x2, y2 - radius], outline, width)