from typing import Dict, Any

TOOL_DEFAULTS: Dict[str, Dict[str, Any]] = {
    'text': {
        'properties': {
            'text': 'New Text',
            'font': 'Arial',
            'fontSize': 12,
            'fill': 'black',
            'bold': False,
            'italic': False
        }
    },
    'shape': {
        'properties': {
            'width': 100,
            'height': 100,
            'fill': 'white',
            'outline': 'black'
        }
    },
    'image': {
        'properties': {
            'width': 100,
            'height': 100,
            'image_path': ''
        }
    }
}

TOOL_CONFIGS = [
    {
        'name': 'select',
        'icon': 'select_icon.png',
        'cursor': 'arrow',
        'label': 'Select (V)',
        'shortcut': 'v'
    },
    {
        'name': 'move',
        'icon': 'move_icon.png',
        'cursor': 'fleur',
        'label': 'Move (M)',
        'shortcut': 'm'
    },
    {
        'name': 'resize',
        'icon': 'resize_icon.png',
        'cursor': 'sizing',
        'label': 'Resize (R)',
        'shortcut': 'r'
    },
    {
        'name': 'text',
        'icon': 'text_icon.png',
        'cursor': 'xterm',
        'label': 'Text (T)',
        'shortcut': 't'
    },
    {
        'name': 'shape',
        'icon': 'shape_icon.png',
        'cursor': 'crosshair',
        'label': 'Shape (S)',
        'shortcut': 's'
    },
    {
        'name': 'image',
        'icon': 'image_icon.png',
        'cursor': 'plus',
        'label': 'Image (I)',
        'shortcut': 'i'
    }
] 