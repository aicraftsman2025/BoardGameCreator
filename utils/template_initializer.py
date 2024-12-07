import json

DEFAULT_TEMPLATES = [
    {
        'name': 'Standard Playing Card',
        'type': 'Cards',
        'category': 'playing_cards',
        'properties': {
            'dimensions': {'width': 63, 'height': 88},
            'corners': 'rounded',
            'layout': {
                'areas': [
                    {'name': 'top_value', 'x': 5, 'y': 5, 'width': 15, 'height': 15},
                    {'name': 'center_art', 'x': 10, 'y': 20, 'width': 43, 'height': 48},
                    {'name': 'bottom_value', 'x': 43, 'y': 68, 'width': 15, 'height': 15}
                ]
            }
        }
    },
    {
        'name': 'Hexagonal Tile',
        'type': 'Tokens',
        'category': 'board_tiles',
        'properties': {
            'dimensions': {'width': 50, 'height': 57.74},
            'shape': 'hexagon',
            'layout': {
                'areas': [
                    {'name': 'main_content', 'x': 5, 'y': 5, 'width': 40, 'height': 47.74}
                ]
            }
        }
    }
]

def initialize_default_templates(db):
    
    for template in DEFAULT_TEMPLATES:
        db.execute("""
            INSERT OR IGNORE INTO templates 
            (name, type, category, properties, is_default)
            VALUES (?, ?, ?, ?, ?)
        """, (
            template['name'],
            template['type'],
            template['category'],
            json.dumps(template['properties']),
            True
        ))
    db.conn.commit()