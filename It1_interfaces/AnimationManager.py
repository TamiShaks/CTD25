"""
AnimationManager - Handles game animations
Manages animation states and transitions throughout the game
"""
from typing import List, Dict, Any
from It1_interfaces.EventTypes import GAME_STARTED, GAME_ENDED
import time

class AnimationManager:
    def __init__(self):
        """Initialize animation manager."""
        self.active_animations: List[Dict[str, Any]] = []
        self.game_state: str = "waiting"
        self.start_time: float = 0.0
    
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """Update animation state based on game events."""
        if event_type == GAME_STARTED:
            self.game_state = "playing"
            game_time = data.get("time", 0) if data else 0
            
            # You could add startup animations here
            # self.add_game_start_animation()
            
        elif event_type == GAME_ENDED:
            self.game_state = "ended"
            game_time = data.get("time", 0) if data else 0
            
            # You could add ending animations here
            # self.add_game_end_animation()
            self.cleanup_animations()
    
    def add_animation(self, animation_type: str, duration_ms: int, target: Any = None, 
                     properties: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Add a new animation to the queue.
        
        Args:
            animation_type: Type of animation to add
            duration_ms: Duration of animation in milliseconds
            target: Optional target object for the animation
            properties: Optional additional animation properties
            
        Returns:
            The created animation dictionary
            
        Raises:
            ValueError: If duration_ms is less than or equal to 0
        """
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
        self.active_animations.append(animation)
        return animation
    
    def update_animations(self, current_time_ms: int) -> List[Dict[str, Any]]:
        """
        Update all active animations and return completed ones.
        
        Args:
            current_time_ms: Current game time in milliseconds
            
        Returns:
            List of completed animations that were removed
        """
        completed_animations = []
        active_animations = []
        
        for anim in self.active_animations:
            elapsed_time = current_time_ms - anim["start_time"]
            if elapsed_time >= anim["duration"]:
                anim["completed"] = True
                completed_animations.append(anim)
            else:
                anim["progress"] = elapsed_time / anim["duration"]
                active_animations.append(anim)
        
        self.active_animations = active_animations
        return completed_animations
    
    def cleanup_animations(self) -> None:
        """Clear all active animations."""
        count = len(self.active_animations)
        self.active_animations.clear()
    
    def get_animation_count(self) -> int:
        """Get number of active animations."""
        return len(self.active_animations)
        
    def is_animating(self) -> bool:
        """Check if there are any active animations."""
        return len(self.active_animations) > 0
        
    def get_animation_by_id(self, animation_id: str) -> Dict[str, Any]:
        """
        Get an animation by its ID.
        
        Args:
            animation_id: The ID of the animation to find
            
        Returns:
            The animation dictionary if found, None otherwise
        """
        for animation in self.active_animations:
            if animation.get("id") == animation_id:
                return animation
        return None
        
    def remove_animation(self, animation_id: str) -> bool:
        """
        Remove an animation by its ID.
        
        Args:
            animation_id: The ID of the animation to remove
            
        Returns:
            True if animation was found and removed, False otherwise
        """
        for i, animation in enumerate(self.active_animations):
            if animation.get("id") == animation_id:
                self.active_animations.pop(i)
                return True
        return False
