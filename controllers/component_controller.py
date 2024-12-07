import json
from models.component import Component

class ComponentController:
    def __init__(self, db):
        self.db = db
    
    def create_component(self, project_id: int, component_data: dict) -> Component:
        query = """
            INSERT INTO components 
            (project_id, type, name, description, properties)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor = self.db.execute(
            query,
            (
                project_id,
                component_data['type'],
                component_data['name'],
                component_data.get('description', ''),
                json.dumps(component_data.get('properties', {}))
            )
        )
        self.db.commit()
        
        return self.get_component_by_id(cursor.lastrowid)
    
    def get_component_by_id(self, component_id: int) -> Component:
        query = "SELECT * FROM components WHERE component_id = ?"
        cursor = self.db.execute(query, (component_id,))
        row = cursor.fetchone()
        return Component.from_db_row(row) if row else None
    
    def get_project_components(self, project_id: int) -> list:
        query = "SELECT * FROM components WHERE project_id = ?"
        cursor = self.db.execute(query, (project_id,))
        return [Component.from_db_row(row) for row in cursor.fetchall()]
    
    def update_component(self, component_id: int, component_data: dict) -> Component:
        query = """
            UPDATE components 
            SET type = ?, name = ?, description = ?, properties = ?
            WHERE component_id = ?
        """
        self.db.execute(
            query,
            (
                component_data['type'],
                component_data['name'],
                component_data.get('description', ''),
                json.dumps(component_data.get('properties', {})),
                component_id
            )
        )
        self.db.commit()
        
        return self.get_component_by_id(component_id)
    
    def delete_component(self, component_id: int) -> bool:
        query = "DELETE FROM components WHERE component_id = ?"
        self.db.execute(query, (component_id,))
        self.db.commit()
        return True 