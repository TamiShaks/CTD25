# from Command import Command
# from Moves import Moves
# from Graphics import Graphics
# from Physics import Physics
# from typing import Dict
# import time


# class State:
#     def __init__(self, moves: Moves, graphics: Graphics, physics: Physics):
#         """Initialize state with moves, graphics, and physics components."""
#         pass

#     def set_transition(self, event: str, target: "State"):
#         """Set a transition from this state to another state on an event."""
#         pass

#     def reset(self, cmd: Command):
#         """Reset the state with a new command."""
#         pass

#     def can_transition(self, now_ms: int) -> bool:           # customise per state
#         """Check if the state can transition."""
#         pass

#     def get_state_after_command(self, cmd: Command, now_ms: int) -> "State":
#         """Get the next state after processing a command."""
#         pass

#     def update(self, now_ms: int) -> "State":
#         """Update the state based on current time."""
#         pass

#     def get_command(self) -> Command:
#         """Get the current command for this state."""
#         pass

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
        self.transitions: Dict[str, "State"] = {}
        self.current_command: Command = None
        self.state_start_time = 0

    def set_transition(self, event: str, target: "State"):
        """Set a transition from this state to another state on an event."""
        self.transitions[event] = target

    def reset(self, cmd: Command):
        """Reset the state with a new command."""
        self.current_command = cmd
        self.state_start_time = cmd.timestamp
        
        # Reset all components
        self.graphics.reset(cmd)
        self.physics.reset(cmd)

    def can_transition(self, now_ms: int) -> bool:
        """Check if the state can transition."""
        # Default implementation: can transition when not animating
        return not self.graphics.is_playing and not self.physics.is_moving

    def get_state_after_command(self, cmd: Command, now_ms: int) -> "State":
        """Get the next state after processing a command."""
        # Look for transition based on command type
        if cmd.type in self.transitions:
            next_state = self.transitions[cmd.type]
            next_state.reset(cmd)
            return next_state
        
        # No transition found, stay in current state
        return self

    def update(self, now_ms: int) -> "State":
        """Update the state based on current time."""
        # Update components
        self.graphics.update(now_ms)
        self.physics.update(now_ms)
        
        # Check for automatic transitions
        if self.can_transition(now_ms):
            # Check for "complete" transition after animation finishes
            if "complete" in self.transitions:
                next_state = self.transitions["complete"]
                # Create a dummy command for the transition
                completion_cmd = Command(
                    timestamp=now_ms,
                    piece_id=self.current_command.piece_id if self.current_command else "",
                    type="complete",
                    params=[]
                )
                next_state.reset(completion_cmd)
                return next_state
        
        return self

    def get_command(self) -> Command:
        """Get the current command for this state."""
        return self.current_command