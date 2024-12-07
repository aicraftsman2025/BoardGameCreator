from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict

@dataclass
class Project:
    project_id: Optional[int]
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    settings_id: Optional[int] = None
    
    @classmethod
    def from_db_row(cls, row):
        return cls(
            project_id=row['project_id'],
            name=row['name'],
            description=row['description'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )
    
    def to_dict(self):
        return {
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'settings_id': self.settings_id
        } 