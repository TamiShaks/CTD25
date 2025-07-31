"""Game animation manager with queue and state tracking."""
from typing import List, Dict, Any
from EventTypes import GAME_STARTED, GAME_ENDED
import time

class GameAnimationQueue:
    def __init__(self):
        self.animations: List[Dict[str, Any]] = []
        self.game_state: str = "waiting"
        self.start_time: float = 0.0
    
    def handle_game_event(self, event_type: str, data: Dict[str, Any]) -> None:
        if event_type == GAME_STARTED:
            self.game_state = "playing"
        elif event_type == GAME_ENDED:
            self.game_state = "ended"
            self.clear_all_animations()
    
    def add_animation(self, animation_type: str, duration_ms: int, target: Any = None, 
                     properties: Dict[str, Any] = None) -> Dict[str, Any]:
        if duration_ms <= 0:
            raise ValueError("Animation duration must be positive")
            
        animation = {
            "type": animation_type,
            "duration": duration_ms,
            "start_time": time.time() * 1000,
            "target": target,
            "completed": False,
            "progress": 0.0,
            "properties": properties or {},
            "id": f"{animation_type}_{time.time()}"
        }
        self.animations.append(animation)
        return animation
    
    def update_all_animations(self, current_time_ms: int) -> List[Dict[str, Any]]:
        completed = []
        active = []
        
        for anim in self.animations:
            elapsed = current_time_ms - anim["start_time"]
            if elapsed >= anim["duration"]:
                anim["completed"] = True
                completed.append(anim)
            else:
                anim["progress"] = elapsed / anim["duration"]
                active.append(anim)
        
        self.animations = active
        return completed
    
    def clear_all_animations(self) -> None:
        self.animations.clear()
    
    def get_active_count(self) -> int:
        return len(self.animations)
        
    def has_active_animations(self) -> bool:
        return bool(self.animations)
        
    def find_animation_by_id(self, animation_id: str) -> Dict[str, Any]:
        for animation in self.animations:
            if animation.get("id") == animation_id:
                return animation
        return None
        
    def remove_animation_by_id(self, animation_id: str) -> bool:
        for i, animation in enumerate(self.animations):
            if animation.get("id") == animation_id:
                self.animations.pop(i)
                return True
        return False

# Backward compatibility methods
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """Backward compatibility for EventBus."""
        return self.handle_game_event(event_type, data)

# Backward compatibility
AnimationManager = GameAnimationQueue
