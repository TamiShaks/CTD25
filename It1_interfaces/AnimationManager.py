from It1_interfaces.EventTypes import GAME_STARTED, GAME_ENDED
import time

class AnimationManager:
    def __init__(self):
        self.active_animations = []
        self.game_state = "waiting"
    
    def update(self, event_type, data):
        if event_type == GAME_STARTED:
            self.game_state = "playing"
            game_time = data.get("time", 0)
            
            # You could add startup animations here
            # self.add_game_start_animation()
            
        elif event_type == GAME_ENDED:
            self.game_state = "ended"
            game_time = data.get("time", 0)
            
            # You could add ending animations here
            # self.add_game_end_animation()
            self.cleanup_animations()
    
    def add_animation(self, animation_type, duration_ms, target=None):
        """Add a new animation to the queue."""
        animation = {
            "type": animation_type,
            "duration": duration_ms,
            "start_time": time.time() * 1000,
            "target": target
        }
        self.active_animations.append(animation)
    
    def update_animations(self, current_time_ms):
        """Update all active animations."""
        completed = []
        for i, animation in enumerate(self.active_animations):
            elapsed = current_time_ms - animation["start_time"]
            if elapsed >= animation["duration"]:
                completed.append(i)
        
        # Remove completed animations (reverse order to maintain indices)
        for i in reversed(completed):
            animation = self.active_animations.pop(i)
    
    def cleanup_animations(self):
        """Clean up all animations."""
        count = len(self.active_animations)
        self.active_animations.clear()
    
    def get_animation_count(self):
        """Get number of active animations."""
        return len(self.active_animations)
