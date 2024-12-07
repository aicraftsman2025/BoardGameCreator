from dataclasses import dataclass
from typing import Dict, Optional
import json

@dataclass
class Component:
    component_id: Optional[int]
    project_id: int
    type: str  # 'card', 'token', 'board'
    name: str
    description: str
    properties: Dict
    
    @classmethod
    def from_db_row(cls, row):
        return cls(
            component_id=row['component_id'],
            project_id=row['project_id'],
            type=row['type'],
            name=row['name'],
            description=row['description'],
            properties=json.loads(row['properties'])
        )
    
    def to_dict(self):
        return {
            'component_id': self.component_id,
            'project_id': self.project_id,
            'type': self.type,
            'name': self.name,
            'description': self.description,
            'properties': self.properties
        } 