import json
import os
from pathlib import Path
from datetime import datetime
from config import get_config
class TemplateManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.config = get_config()  # Get config instance
        self.templates_dir = self.config.USER_DATA_DIR / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
    def save_template(self, name: str, template_data: dict) -> bool:
        """
        Save a template to storage
        
        Args:
            name: Template name
            template_data: Template configuration and elements
        """
        try:
            # Add metadata
            template_data['metadata'] = {
                'name': name,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Create filename from template name
            filename = f"{name.lower().replace(' ', '_')}.json"
            file_path = self.templates_dir / filename
            
            # Save template to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=4)
            
            return True
        except Exception as e:
            print(f"Error saving template: {e}")
            return False
    
    def load_template(self, name: str) -> dict:
        """
        Load a template by name
        
        Args:
            name: Template name to load
            
        Returns:
            Template data dictionary or None if not found
        """
        try:
            filename = f"{name.lower().replace(' ', '_')}.json"
            file_path = self.templates_dir / filename
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Template not found: {name}")
            return None
        except Exception as e:
            print(f"Error loading template: {e}")
            return None
    
    def list_templates(self, category: str = None) -> list:
        """
        List all available templates, optionally filtered by category
        
        Args:
            category: Optional category filter
            
        Returns:
            List of template names
        """
        templates = []
        for file in self.templates_dir.glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if category is None or data.get('category', '').lower() == category.lower():
                        templates.append(data['metadata']['name'])
            except Exception as e:
                print(f"Error reading template {file}: {e}")
        return sorted(templates)
    
    def delete_template(self, name: str) -> bool:
        """
        Delete a template
        
        Args:
            name: Template name to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            filename = f"{name.lower().replace(' ', '_')}.json"
            file_path = self.templates_dir / filename
            file_path.unlink()
            return True
        except FileNotFoundError:
            print(f"Template not found: {name}")
            return False
        except Exception as e:
            print(f"Error deleting template: {e}")
            return False
    
    def update_template(self, name: str, template_data: dict) -> bool:
        """
        Update an existing template
        
        Args:
            name: Template name to update
            template_data: New template data
        """
        try:
            existing = self.load_template(name)
            if existing:
                # Preserve creation date, update modified date
                template_data['metadata'] = {
                    'name': name,
                    'created_at': existing['metadata']['created_at'],
                    'updated_at': datetime.now().isoformat()
                }
                return self.save_template(name, template_data)
            return False
        except Exception as e:
            print(f"Error updating template: {e}")
            return False

    def get_template_metadata(self, name: str) -> dict:
        """
        Get template metadata without loading full template
        
        Args:
            name: Template name
            
        Returns:
            Template metadata dictionary
        """
        template = self.load_template(name)
        return template.get('metadata') if template else None 