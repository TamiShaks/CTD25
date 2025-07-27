from typing import Dict, List, Callable, Any
from dataclasses import dataclass

@dataclass
class Event:
    """Simple event class."""
    name: str
    data: Any = None
    timestamp: int = 0

class EventBus:
    """Simple event bus for game events."""
    
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_name: str, callback: Callable):
        """Subscribe to an event."""
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(callback)
    
    def publish(self, event: Event):
        """Publish an event to all subscribers."""
        if event.name in self.listeners:
            for callback in self.listeners[event.name]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in event callback: {e}")
    
    def unsubscribe(self, event_name: str, callback: Callable):
        """Unsubscribe from an event."""
        if event_name in self.listeners and callback in self.listeners[event_name]:
            self.listeners[event_name].remove(callback)