from dataclasses import dataclass
from typing import Any, Callable, Dict, List
import threading


@dataclass
class Event:
    type: str
    data: Any = None
    timestamp: int = 0


class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()
    
    def subscribe(self, event_type: str, callback: Callable):
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(callback)
    
    def publish(self, event: Event):
        with self._lock:
            subscribers = self._subscribers.get(event.type, [])
            for callback in subscribers:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in event callback: {e}")