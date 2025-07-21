from typing import Tuple, Optional
from Command import Command
import math

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
        
    def reset(self, cmd: Command):
        """Reset physics state with a new command."""
        if cmd.type == "Move" and cmd.params:
            self.target_cell = cmd.params[0]
            self.is_moving = True
            self.move_start_time = cmd.timestamp
            
            # Calculate movement duration based on distance
            dr = abs(self.target_cell[0] - self.current_cell[0])
            dc = abs(self.target_cell[1] - self.current_cell[1])
            distance = max(dr, dc)  # Use Chebyshev distance
            self.move_duration = int(distance / self.SLIDE_CELLS_PER_SEC * 1000)  # Convert to ms

    def update(self, now_ms: int):
        """Update physics state based on current time."""
        if self.is_moving:
            elapsed = now_ms - self.move_start_time
            if elapsed >= self.move_duration:
                # Movement complete
                self.current_cell = self.target_cell
                self.is_moving = False
            # Otherwise, piece is still moving (interpolation handled in get_pos)

    def can_be_captured(self) -> bool:
        """Check if this piece can be captured."""
        return not self.is_moving  # Can't capture moving pieces

    def can_capture(self) -> bool:
        """Check if this piece can capture other pieces."""
        return not self.is_moving  # Can't capture while moving

    def get_pos(self) -> Tuple[int, int]:
        """Current pixel-space upper-left corner of the sprite."""
        if self.is_moving and self.move_duration > 0:
            # Interpolate between current and target positions
            elapsed = min(self.move_duration, time.time() * 1000 - self.move_start_time)
            progress = elapsed / self.move_duration
            
            start_x = self.current_cell[1] * self.board.cell_W_pix
            start_y = self.current_cell[0] * self.board.cell_H_pix
            target_x = self.target_cell[1] * self.board.cell_W_pix  
            target_y = self.target_cell[0] * self.board.cell_H_pix
            
            current_x = int(start_x + (target_x - start_x) * progress)
            current_y = int(start_y + (target_y - start_y) * progress)
            
            return (current_x, current_y)
        else:
            # Return current cell position
            return (self.current_cell[1] * self.board.cell_W_pix, 
                   self.current_cell[0] * self.board.cell_H_pix)

