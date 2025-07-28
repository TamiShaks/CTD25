from typing import Tuple, Optional
from .Command import Command
from .Board import Board
import time

class Physics:
    SLIDE_CELLS_PER_SEC = 4.0

    def __init__(self, start_cell: Tuple[int, int], board: "Board", speed_m_s: float = 1.0):
        """Initialize physics with starting cell, board, and speed."""
        self.start_cell = start_cell
        self.current_cell = start_cell
        self.target_cell = start_cell
        self.board = board
        self.speed_m_s = speed_m_s
        self.is_moving = False
        self.move_start_time = 0
        self.move_duration = 0
        
    def copy(self) -> "Physics":
        """Create a copy of this physics object."""
        new_physics = Physics(self.start_cell, self.board, self.speed_m_s)
        new_physics.current_cell = self.current_cell
        new_physics.target_cell = self.target_cell
        new_physics.is_moving = self.is_moving
        new_physics.move_start_time = self.move_start_time
        new_physics.move_duration = self.move_duration
        return new_physics
        
    def reset(self, cmd: Command):
        """Reset physics state with a new command."""
        if cmd.type == "Move" and cmd.params:
            old_cell = self.current_cell
            self.target_cell = cmd.params[1]
            self.is_moving = True
            self.move_start_time = cmd.timestamp

            dr = abs(self.target_cell[0] - self.current_cell[0])
            dc = abs(self.target_cell[1] - self.current_cell[1])
            distance = max(dr, dc)
            self.move_duration = int(distance / self.SLIDE_CELLS_PER_SEC * 1000)
            
        elif cmd.type == "Jump" and cmd.params:
            # For jump, stay in the same position but mark as "moving" for animation
            self.target_cell = self.current_cell  # Jump in place
            self.is_moving = True
            self.move_start_time = cmd.timestamp
            self.move_duration = 1500  # 1.5 seconds for jump animation
            
        else:
            # For non-move commands (like idle, complete, timeout), stop any movement
            # but KEEP the current position - don't reset to start_cell!
            self.is_moving = False

    def update(self, now_ms: int) -> bool:
        """Update physics state based on current time. Returns True if movement was just completed."""
        if self.is_moving:
            elapsed = now_ms - self.move_start_time

            if elapsed >= self.move_duration:
                # Movement complete - this is the critical change!
                self.current_cell = self.target_cell
                self.is_moving = False
                return True  # Signal that movement was just completed
            else:
                # Calculate progress and interpolate position
                progress = elapsed / self.move_duration
                # Note: We keep current_cell as the starting position until movement is complete
                # The actual pixel position is calculated in get_pos()
        
        return False  # No movement completion

    def can_be_captured(self) -> bool:
        """Check if this piece can be captured."""
        return not self.is_moving  # Can't capture moving pieces

    def can_capture(self) -> bool:
        """Check if this piece can capture other pieces."""
        return not self.is_moving  # Can't capture while moving

    def get_pos(self, now_ms: int = None) -> Tuple[int, int]:
        """Current pixel-space upper-left corner of the sprite."""
        if self.is_moving and self.move_duration > 0:
            # Use the provided time or calculate current time
            if now_ms is None:
                now_ms = int(time.time() * 1000)
            
            # Interpolate between current and target positions
            elapsed = now_ms - self.move_start_time
            elapsed = max(0, min(self.move_duration, elapsed))
            progress = elapsed / self.move_duration if self.move_duration > 0 else 1.0

            start_x = self.current_cell[1] * self.board.cell_W_pix
            start_y = self.current_cell[0] * self.board.cell_H_pix
            target_x = self.target_cell[1] * self.board.cell_W_pix
            target_y = self.target_cell[0] * self.board.cell_H_pix

            current_x = int(start_x + (target_x - start_x) * progress)
            current_y = int(start_y + (target_y - start_y) * progress)

            return (current_x, current_y)
        else:
            pos = (self.current_cell[1] * self.board.cell_W_pix, 
                   self.current_cell[0] * self.board.cell_H_pix)
            return pos
