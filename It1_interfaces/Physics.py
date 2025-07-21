# from typing import Tuple, Optional
# from Command import Command
# import math
# class Physics:
#     SLIDE_CELLS_PER_SEC = 4.0        # tweak to make all pieces slower/faster

#     def __init__(self, start_cell: Tuple[int, int],
#                  board: "Board", speed_m_s: float = 1.0):
#         """Initialize physics with starting cell, board, and speed."""
#         pass

#     def reset(self, cmd: Command):
#         """Reset physics state with a new command."""
#         pass

#     def update(self, now_ms: int):
#         """Update physics state based on current time."""
#         pass

#     def can_be_captured(self) -> bool: 
#         """Check if this piece can be captured."""
#         pass
        
#     def can_capture(self) -> bool:     
#         """Check if this piece can capture other pieces."""
#         pass 

#     def get_pos(self) -> Tuple[int, int]:
#         """
#         Current pixel-space upper-left corner of the sprite.
#         Uses the sub-pixel coordinate computed in update();
#         falls back to the square's origin before the first update().
#         """
#         pass

from typing import Tuple, Optional
from Command import Command
import math
import time

class Physics:
    SLIDE_CELLS_PER_SEC = 4.0

    def __init__(self, start_cell: Tuple[int, int], board: "Board", speed_m_s: float = 1.0):
        """Initialize physics with starting cell, board, and speed."""
        self.start_cell = start_cell
        self.current_cell = start_cell
        self.target_cell = start_cell
        self.board = board
        self.speed_multiplier = speed_m_s
        
        # Animation state
        self.is_moving = False
        self.move_start_time = 0
        self.move_duration = 0
        self.start_pos = self._cell_to_pixel(start_cell)
        self.current_pos = self.start_pos
        self.target_pos = self.start_pos
        
        # State flags
        self._can_be_captured = True
        self._can_capture = True

    def _cell_to_pixel(self, cell: Tuple[int, int]) -> Tuple[int, int]:
        """Convert cell coordinates to pixel coordinates."""
        row, col = cell
        x = col * self.board.cell_W_pix
        y = row * self.board.cell_H_pix
        return x, y

    def reset(self, cmd: Command):
        """Reset physics state with a new command."""
        if cmd.type == "Move" and len(cmd.params) >= 2:
            # Parse move command: ["e2", "e4"] or [(row1,col1), (row2,col2)]
            if isinstance(cmd.params[0], str):
                # Chess notation - convert to coordinates if needed
                # For now, assume direct coordinate format
                pass
            elif isinstance(cmd.params[0], tuple) and len(cmd.params[0]) == 2:
                start_cell, end_cell = cmd.params[0], cmd.params[1]
                self.start_cell = start_cell
                self.target_cell = end_cell
                
                # Calculate movement
                self.start_pos = self._cell_to_pixel(start_cell)
                self.target_pos = self._cell_to_pixel(end_cell)
                
                # Calculate duration based on distance
                dr = abs(end_cell[0] - start_cell[0])
                dc = abs(end_cell[1] - start_cell[1])
                distance = max(dr, dc)  # Use Chebyshev distance
                
                self.move_duration = int((distance / self.SLIDE_CELLS_PER_SEC) * 1000 / self.speed_multiplier)
                self.move_start_time = cmd.timestamp
                self.is_moving = True

    def update(self, now_ms: int):
        """Update physics state based on current time."""
        if not self.is_moving:
            return
            
        elapsed = now_ms - self.move_start_time
        
        if elapsed >= self.move_duration:
            # Movement complete
            self.current_pos = self.target_pos
            self.current_cell = self.target_cell
            self.is_moving = False
        else:
            # Interpolate position
            t = elapsed / self.move_duration
            # Smooth interpolation
            t = 0.5 * (1 - math.cos(math.pi * t))
            
            start_x, start_y = self.start_pos
            target_x, target_y = self.target_pos
            
            current_x = int(start_x + (target_x - start_x) * t)
            current_y = int(start_y + (target_y - start_y) * t)
            
            self.current_pos = (current_x, current_y)

    def can_be_captured(self) -> bool:
        """Check if this piece can be captured."""
        return self._can_be_captured and not self.is_moving

    def can_capture(self) -> bool:
        """Check if this piece can capture other pieces."""
        return self._can_capture and not self.is_moving

    def get_pos(self) -> Tuple[int, int]:
        """Current pixel-space upper-left corner of the sprite."""
        return self.current_pos