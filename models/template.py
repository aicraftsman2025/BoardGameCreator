from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict
import json

@dataclass
class Template:
    template_id: int
    name: str
    description: str
    layout_data: Dict
    created_at: datetime
    updated_at: datetime
    
    @property
    def id(self) -> int:
        """Alias for template_id to maintain compatibility"""
        return self.template_id
    
    @classmethod
    def from_db_row(cls, row):
        return cls(
            template_id=row['template_id'],
            name=row['name'],
            description=row['description'],
            layout_data=json.loads(row['layout_data']),
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )
    
    def to_dict(self):
        return {
            'template_id': self.template_id,
            'name': self.name,
            'description': self.description,
            'layout_data': self.layout_data,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 