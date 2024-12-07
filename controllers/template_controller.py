import os
import json
from datetime import datetime
from models.template import Template
from models.template_manager import TemplateManager
from typing import Optional, List

class TemplateController:
    def __init__(self, db_manager):
        self.template_manager = TemplateManager(db_manager)
    
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