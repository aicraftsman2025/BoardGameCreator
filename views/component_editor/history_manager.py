from typing import List, Dict, Any, Optional
from .events.event_types import EventType

import copy

class HistoryState:
    def __init__(self, elements, background_color):
        self.elements = copy.deepcopy(elements)
        self.background_color = background_color

class HistoryManager:
    def __init__(self, event_manager):
        self.event_manager = event_manager
        self.history: List[HistoryState] = []
        self.current_index: int = -1
        self.max_history: int = 50
    
    def push_state(self, elements: List[Dict[str, Any]], background_color: str) -> None:
        """Push a new state to history"""
        state = HistoryState(elements, background_color)
        
        # If we're not at the end of the history, truncate the future states
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
        
        # Add new state
        self.history.append(state)
        self.current_index += 1
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.current_index -= 1
        
        # Emit state change event
        self._emit_state_change()
    
    def undo(self) -> Optional[HistoryState]:
        """Undo the last action"""
        if self.can_undo():
            self.current_index -= 1
            self._emit_state_change()
            return self.history[self.current_index]
        return None
    
    def redo(self) -> Optional[HistoryState]:
        """Redo the last undone action"""
        if self.can_redo():
            self.current_index += 1
            self._emit_state_change()
            return self.history[self.current_index]
        return None
    
    def can_undo(self) -> bool:
        """Check if undo is available"""
        return self.current_index > 0
    
    def can_redo(self) -> bool:
        """Check if redo is available"""
        return self.current_index < len(self.history) - 1
    
    def _emit_state_change(self) -> None:
        """Emit state change event"""
        self.event_manager.emit(EventType.STATE_CHANGED, {
            'can_undo': self.can_undo(),
            'can_redo': self.can_redo()
        })
    
    def clear(self) -> None:
        """Clear history"""
        self.history.clear()
        self.current_index = -1
        self._emit_state_change() 