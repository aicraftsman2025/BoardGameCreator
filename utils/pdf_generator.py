from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A3, LETTER, LEGAL
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from PIL import Image
import io

class PDFGenerator:
    def __init__(self):
        self.page_sizes = {
            'A4': A4,
            'A3': A3,
            'LETTER': LETTER,
            'LEGAL': LEGAL
        }
    
    def create_component_pdf(self, components: list, output_path: str, settings: dict):
        """Create PDF with multiple components"""
        # Get page size
        page_size = self.page_sizes.get(settings.get('page_size', 'A4'))
        
        # Create PDF
        c = canvas.Canvas(output_path, pagesize=page_size)
        
        # Calculate page margins and grid layout
        margin = 20 * mm
        available_width = page_size[0] - (2 * margin)
        available_height = page_size[1] - (2 * margin)
        
        # Process each component
        x, y = margin, page_size[1] - margin
        for component in components:
            # Add component to PDF
            self._add_component(c, component, x, y)
            
            # Update position for next component
            x += component.get('width', 0) * mm + 10
            if x + component.get('width', 0) * mm > available_width:
                x = margin
                y -= component.get('height', 0) * mm + 10
                
                # Check if new page needed
                if y - component.get('height', 0) * mm < margin:
                    c.showPage()
                    y = page_size[1] - margin
        
        c.save()
        return output_path
    
    def _add_component(self, canvas, component: dict, x: float, y: float):
        """Add a single component to the PDF"""
        # Draw component outline
        width = component.get('width', 0) * mm
        height = component.get('height', 0) * mm
        canvas.rect(x, y - height, width, height)
        
        # Add component content
        if component.get('image'):
            self._add_image(canvas, component['image'], x, y, width, height)
        
        if component.get('text'):
            self._add_text(canvas, component['text'], x, y, width, height)
    
    def _add_image(self, canvas, image_path: str, x: float, y: float, width: float, height: float):
        """Add image to PDF"""
        try:
            img = Image.open(image_path)
            # Scale image to fit
            img_width, img_height = img.size
            scale = min(width/(img_width * mm), height/(img_height * mm))
            
            # Convert PIL Image to reportlab ImageReader
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_reader = ImageReader(io.BytesIO(img_buffer.getvalue()))
            
            # Draw image
            canvas.drawImage(img_reader, x, y - height, width=width, height=height)
        except Exception as e:
            print(f"Error adding image to PDF: {str(e)}")
    
    def _add_text(self, canvas, text: str, x: float, y: float, width: float, height: float):
        """Add text to PDF"""
        canvas.setFont("Helvetica", 12)
        # Simple text addition - can be enhanced for more complex text layouts
        canvas.drawString(x + 5, y - 15, text) 