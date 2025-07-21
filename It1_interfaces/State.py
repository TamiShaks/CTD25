from Command import Command
from Moves import Moves
from Graphics import Graphics  
from Physics import Physics
from typing import Dict
import time

class State:
    def __init__(self, moves: Moves, graphics: Graphics, physics: Physics):
        """Initialize state with moves, graphics, and physics components."""
        self.moves = moves
        self.graphics = graphics
        self.physics = physics
        self.transitions = {}
        self.state_start_time = 0
        self.current_command = None
        
        # State-specific properties
        self.is_rest_state = False
        self.rest_duration_ms = 0

    def set_transition(self, event: str, target: "State"):
        """Set a transition from this state to another state on an event."""
        self.transitions[event] = target

    def reset(self, cmd: Command):
        """Reset the state with a new command."""
        self.current_command = cmd
        self.state_start_time = cmd.timestamp
        self.graphics.reset(cmd)
        self.physics.reset(cmd)

    def can_transition(self, now_ms: int) -> bool:
        """Check if the state can transition."""
        if self.is_rest_state:
            # Rest states can only transition after their duration expires
            elapsed = now_ms - self.state_start_time
            return elapsed >= self.rest_duration_ms
        return True

    def get_state_after_command(self, cmd: Command, now_ms: int) -> "State":
        """Get the next state after processing a command."""
        if not self.can_transition(now_ms):
            return self  # Stay in current state if can't transition
            
        if cmd.type in self.transitions:
            next_state = self.transitions[cmd.type].copy()  
            next_state.reset(cmd)
            return next_state
        return self

    def update(self, now_ms: int) -> "State":
        """Update the state based on current time."""
        self.graphics.update(now_ms)
        self.physics.update(now_ms)
        
        # Check for automatic transitions (like rest state expiring)
        if self.is_rest_state and self.can_transition(now_ms):
            if "timeout" in self.transitions:
                next_state = self.transitions["timeout"].copy()
                # Create a dummy command for the transition
                dummy_cmd = Command(now_ms, "", "timeout", [])
                next_state.reset(dummy_cmd)
                return next_state
                
        return self

    def get_command(self) -> Command:
        """Get the current command for this state."""
        return self.current_command

# Helper function to create rest states
def create_long_rest_state(idle_state: State) -> State:
    """Create a 2-second rest state that transitions back to idle."""
    # Use same components but mark as rest state
    rest_state = State(idle_state.moves, idle_state.graphics.copy(), idle_state.physics)
    rest_state.is_rest_state = True
    rest_state.rest_duration_ms = 2000  # 2 seconds
    rest_state.set_transition("timeout", idle_state)
    return rest_state

def create_short_rest_state(idle_state: State) -> State:
    """Create a 1-second rest state that transitions back to idle."""
    rest_state = State(idle_state.moves, idle_state.graphics.copy(), idle_state.physics)
    rest_state.is_rest_state = True
    rest_state.rest_duration_ms = 1000  # 1 second
    rest_state.set_transition("timeout", idle_state)
    return rest_state