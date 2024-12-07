from typing import Callable, Dict, List, Any
from .event_types import EventType

class EventManager:
    def __init__(self):
        self._listeners: Dict[EventType, List[Callable]] = {}
        
    def subscribe(self, event_type: EventType, listener: Callable) -> None:
        """Subscribe to an event"""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)
        
    def unsubscribe(self, event_type: EventType, listener: Callable) -> None:
        """Unsubscribe from an event"""
        if event_type in self._listeners:
            self._listeners[event_type].remove(listener)
            
    def emit(self, event_type: EventType, data: Any = None) -> None:
        """Emit an event with optional data"""
        if event_type in self._listeners:
            for listener in self._listeners[event_type]:
                listener(data) 