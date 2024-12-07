from enum import Enum, auto

class EventType(Enum):
    # Element Events
    ELEMENT_CREATED = auto()
    ELEMENT_SELECTED = auto()
    ELEMENT_DESELECTED = auto()
    ELEMENT_MOVED = auto()
    ELEMENT_RESIZED = auto()
    ELEMENT_DELETED = auto()
    ELEMENT_EDITED = auto()
    ELEMENT_DOUBLE_CLICKED = auto()
    
    # Tool Events
    TOOL_CHANGED = auto()
    
    # Canvas Events
    CANVAS_CLICKED = auto()
    CANVAS_DRAGGED = auto()
    CANVAS_RELEASED = auto()
    CANVAS_SIZE_CHANGED = auto()
    CANVAS_BACKGROUND_CHANGED = auto()
    
    # Template Events
    TEMPLATE_ACTION = auto()
    
    # Component Events
    SAVE_COMPONENT = auto()
    TYPE_CHANGED = auto()
    UNIT_CHANGED = auto()
    
    # History Events
    UNDO = auto()
    REDO = auto()
    STATE_CHANGED = auto()  # For updating undo/redo buttons state
    
    # Export Events
    EXPORT_COMPONENT = "EXPORT_COMPONENT"
    