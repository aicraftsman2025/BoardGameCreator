import os
import json
from typing import Dict, List

class TemplateLoader:
    def __init__(self, template_dir="assets_static/templates"):
        self.template_dir = template_dir
    
    def load_all_templates(self) -> List[Dict]:
        """Load all templates from the templates directory"""
        templates = []
        
        # Walk through template directory
        for root, _, files in os.walk(self.template_dir):
            for file in files:
                if file.endswith('.json'):
                    template_path = os.path.join(root, file)
                    try:
                        template = self.load_template(template_path)
                        if template:
                            templates.append(template)
                    except Exception as e:
                        print(f"Error loading template {file}: {str(e)}")
        
        return templates
    
    def load_template(self, template_path: str) -> Dict:
        """Load a single template from file"""
        try:
            with open(template_path, 'r') as f:
                template = json.load(f)
            
            # Add template file path to metadata
            template['file_path'] = template_path
            return template
        
        except Exception as e:
            print(f"Error loading template {template_path}: {str(e)}")
            return None
    
    def save_template(self, template: Dict, category: str) -> str:
        """Save a template to file"""
        # Create category directory if it doesn't exist
        category_dir = os.path.join(self.template_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        
        # Generate filename from template name
        filename = template['name'].lower().replace(' ', '_') + '.json'
        template_path = os.path.join(category_dir, filename)
        
        # Save template
        try:
            with open(template_path, 'w') as f:
                json.dump(template, f, indent=4)
            return template_path
        
        except Exception as e:
            print(f"Error saving template: {str(e)}")
            return None 