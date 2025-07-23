from .Board import Board
from .Command import Command
from .State import State
import cv2

class Piece:
    def __init__(self, piece_id: str, init_state: State):
        """Initialize a piece with ID and initial state."""
        self.piece_id = piece_id
        self.current_state = init_state
        self.start_time = 0
        
        # Cooldown system
        self.last_action_time = 0
        self.cooldown_duration = 2000  # 2 seconds in ms
        
    def on_command(self, cmd: Command, now_ms: int):
        """Handle a command for this piece."""
        if cmd.piece_id != self.piece_id:
            return  # Command not for this piece
            
        # Check cooldown
        if now_ms - self.last_action_time < self.cooldown_duration:
            return  # Still in cooldown
            
        # Process command and potentially transition state
        new_state = self.current_state.get_state_after_command(cmd, now_ms)
        if new_state != self.current_state:
            self.current_state = new_state
            self.last_action_time = now_ms

    def reset(self, start_ms: int):
       self.start_time = start_ms
       self.last_action_time = start_ms  # לשים לב לסנכרן עם זמן המשחק
       idle_cmd = Command.create_idle_command(start_ms, self.piece_id)
       self.current_state.reset(idle_cmd)

    def update(self, now_ms: int):
        """Update the piece state based on current time."""
        new_state = self.current_state.update(now_ms)
        if new_state != self.current_state:
            self.current_state = new_state

    def draw_on_board(self, board: Board, now_ms: int):
      """Draw the piece on the board with cooldown overlay (yellow fading)."""
      sprite = self.current_state.graphics.get_img()
      x, y = self.current_state.physics.get_pos()

      try:
        sprite.draw_on(board.img, x, y)

        remaining_cooldown = self.cooldown_duration - (now_ms - self.last_action_time)
        if remaining_cooldown > 0:
            cooldown_ratio = remaining_cooldown / self.cooldown_duration
            import numpy as np
            overlay_height = int(board.cell_H_pix * cooldown_ratio)
            if overlay_height > 0 and board.img.img is not None:
                h, w = board.img.img.shape[:2]
                if y + overlay_height <= h and x + board.cell_W_pix <= w:
                    overlay = board.img.img[y:y + overlay_height, x:x + board.cell_W_pix].copy()
                    yellow_overlay = np.full_like(overlay, (0, 255, 255))  # Yellow in BGR
                    alpha = 0.5
                    blended = cv2.addWeighted(yellow_overlay, alpha, overlay, 1 - alpha, 0)
                    board.img.img[y:y + overlay_height, x:x + board.cell_W_pix] = blended

      except Exception as e:
         print(f"Warning: Could not draw piece {self.piece_id}: {e}")


   