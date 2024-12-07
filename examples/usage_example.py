import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import Database
from controllers.project_controller import ProjectController
from controllers.component_controller import ComponentController
from controllers.asset_controller import AssetController
from utils.template_loader import TemplateLoader
from utils.spreadsheet_handler import SpreadsheetHandler
from utils.pdf_generator import PDFGenerator
from utils.image_processor import ImageProcessor

def main():
    # Initialize database
    db = Database()
    
    # Initialize controllers
    project_controller = ProjectController(db)
    component_controller = ComponentController(db)
    asset_controller = AssetController(db)
    
    # Initialize utilities
    template_loader = TemplateLoader()
    spreadsheet_handler = SpreadsheetHandler()
    pdf_generator = PDFGenerator()
    image_processor = ImageProcessor()
    
    # Create a new project
    project = project_controller.create_project(
        name="Card Game Example",
        description="A simple card game project"
    )
    
    # Load a template
    templates = template_loader.load_all_templates()
    if templates:
        card_template = next(
            (t for t in templates if t['type'] == 'card'),
            None
        )
        
        if card_template:
            # Create a component from template
            component = component_controller.create_component(
                project_id=project.project_id,
                component_data={
                    'type': 'card',
                    'name': 'Example Card',
                    'description': 'An example playing card',
                    'properties': card_template['properties']
                }
            )
            
            # Export component as PDF
            pdf_generator.create_component_pdf(
                [component.to_dict()],
                'example_card.pdf',
                {'page_size': 'A4'}
            )
            
            print("Example project and component created successfully!")

if __name__ == "__main__":
    main() 