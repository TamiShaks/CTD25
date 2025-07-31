from typing import Dict, List, Any, Optional


class GameEventNotificationSystem:
    """Self-documenting event system for coordinating game component communication."""
    
    def __init__(self):
        self.event_type_to_listeners_mapping: Dict[str, List[Any]] = {}

    def register_component_for_event_notifications(self, event_type: str, listening_component) -> None:
        if event_type not in self.event_type_to_listeners_mapping:
            self.event_type_to_listeners_mapping[event_type] = []
        self.event_type_to_listeners_mapping[event_type].append(listening_component)

    def remove_component_from_event_notifications(self, event_type: str, listening_component) -> None:
        if event_type in self.event_type_to_listeners_mapping:
            self.event_type_to_listeners_mapping[event_type].remove(listening_component)
            if not self.event_type_to_listeners_mapping[event_type]:
                del self.event_type_to_listeners_mapping[event_type]

    def broadcast_event_to_all_registered_listeners(self, event_type: str, event_data: Optional[Any] = None) -> None:
        if event_type in self.event_type_to_listeners_mapping:
            for listening_component in self.event_type_to_listeners_mapping[event_type]:
                listening_component.update(event_type, event_data)


# Backward compatibility aliases
EventBus = GameEventNotificationSystem
EventBus.subscribers = property(lambda self: self.event_type_to_listeners_mapping)
EventBus.subscribe = GameEventNotificationSystem.register_component_for_event_notifications  
EventBus.unsubscribe = GameEventNotificationSystem.remove_component_from_event_notifications
EventBus.publish = GameEventNotificationSystem.broadcast_event_to_all_registered_listeners
