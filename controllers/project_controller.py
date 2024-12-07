from datetime import datetime
from models.project import Project

class ProjectController:
    def __init__(self, db):
        self.db = db
    
    def create_project(self, name: str, description: str) -> Project:
        query = """
            INSERT INTO projects (name, description)
            VALUES (?, ?)
        """
        cursor = self.db.execute(query, (name, description))
        self.db.commit()
        
        return self.get_project_by_id(cursor.lastrowid)
    
    def get_project_by_id(self, project_id: int) -> Project:
        query = "SELECT * FROM projects WHERE project_id = ?"
        cursor = self.db.execute(query, (project_id,))
        row = cursor.fetchone()
        return Project.from_db_row(row) if row else None
    
    def get_all_projects(self):
        return self.db.get_all_projects()
    
    def update_project(self, project_id: int, name: str, description: str) -> Project:
        query = """
            UPDATE projects 
            SET name = ?, description = ?, updated_at = ?
            WHERE project_id = ?
        """
        self.db.execute(query, (
            name,
            description,
            datetime.now().isoformat(),
            project_id
        ))
        self.db.commit()
        
        return self.get_project_by_id(project_id)
    
    def delete_project(self, project_id: int) -> bool:
        """Delete project and all its associated components"""
        try:
            # Start a transaction
            self.db.execute("BEGIN TRANSACTION")
            
            # First delete all components associated with the project
            self.db.execute(
                "DELETE FROM components WHERE project_id = ?",
                (project_id,)
            )
            
            # Then delete the project
            self.db.execute(
                "DELETE FROM projects WHERE project_id = ?",
                (project_id,)
            )
            
            # Commit the transaction
            self.db.execute("COMMIT")
            return True
            
        except Exception as e:
            # If anything goes wrong, rollback the transaction
            self.db.execute("ROLLBACK")
            print(f"Error deleting project: {str(e)}")
            return False 