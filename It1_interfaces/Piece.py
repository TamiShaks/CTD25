from .Board import Board
from .Command import Command
from .State import State
import cv2
import numpy as np

class Piece:
    def __init__(self, piece_id: str, init_state: State, piece_type: str):
        """Initialize a piece with ID, initial state, and type."""
        self.piece_id = piece_id
        self.current_state = init_state
        self.piece_type = piece_type
        self.start_time = 0
        
        # Track piece color from piece_id (PW/PB prefix)
        if piece_id.startswith('PW') or piece_id.startswith('RW') or piece_id.startswith('NW') or piece_id.startswith('BW') or piece_id.startswith('QW') or piece_id.startswith('KW'):
            self.color = "White"
        elif piece_id.startswith('PB') or piece_id.startswith('RB') or piece_id.startswith('NB') or piece_id.startswith('BB') or piece_id.startswith('QB') or piece_id.startswith('KB'):
            self.color = "Black"
        else:
            self.color = "Unknown"
        
        # Movement tracking for pawns (first move rule)
        self.move_count = 0
        self.has_moved = False
        
        # Cooldown system
        self.last_action_time = 0
        self.cooldown_duration = 2000  # 2 seconds in ms
        
        
    def on_command(self, cmd: Command, now_ms: int):
        """Handle a command for this piece."""
        if cmd.piece_id != self.piece_id:
            return  # Command not for this piece
        
        
        # Block movement commands during long_rest
        if self.current_state.state == "long_rest" and cmd.type in ["Move", "Jump"]:
            return  # Cannot move during rest
        
        # Check cooldown
        if now_ms - self.last_action_time < self.cooldown_duration:
            return  # Still in cooldown
        
        # Special handling for pawn double move (only on first move)
        if self.piece_type == "P" and cmd.type == "Move":
            source = cmd.get_source_cell()
            target = cmd.get_target_cell()
            if source and target:
                row_diff = abs(target[0] - source[0])
                # If trying to move 2 squares and already moved before
                if row_diff == 2 and self.has_moved:
                    return  # Block double move after first move
                elif row_diff >= 1:  # Any valid move
                    self.has_moved = True  # Mark as moved
            
        # Process command and potentially transition state
        old_state = self.current_state.state
        new_state = self.current_state.get_state_after_command(cmd, now_ms)
        
        if new_state != self.current_state:
            self.current_state = new_state
            self.last_action_time = now_ms
            
            # Track movement for pawns
            if cmd.type in ["Move", "Jump"]:
                self.move_count += 1
                self.has_moved = True
        
        # Reset physics for the current state (whether it changed or not)
        self.current_state.physics.reset(cmd)

    def reset(self, start_ms: int):
        self.start_time = start_ms
        self.last_action_time = start_ms
        # Reset movement tracking
        self.move_count = 0
        self.has_moved = False
        idle_cmd = Command.create_idle_command(start_ms, self.piece_id)
        self.current_state.reset(idle_cmd)

    def update(self, now_ms: int):
        """Update the piece state based on current time."""
        old_state_name = self.current_state.state
        new_state = self.current_state.update(now_ms)
        
        if new_state != self.current_state:
            self.current_state = new_state
        # else:

    def draw_on_board(self, board: Board, now_ms: int):
        """Draw the piece on the board with cooldown overlay (yellow fading)."""
        # Pass timing information for dynamic blue tint
        sprite = self.current_state.graphics.get_img(
            state_start_time=self.current_state.state_start_time,
            rest_duration_ms=self.current_state.rest_duration_ms,
            now_ms=now_ms
        )
        x, y = self.current_state.physics.get_pos(now_ms)  # Pass now_ms to get current position

        try:
            sprite.draw_on(board.img, x, y)

            remaining_cooldown = self.cooldown_duration - (now_ms - self.last_action_time)
            if remaining_cooldown > 0:
                cooldown_ratio = remaining_cooldown / self.cooldown_duration
                overlay_height = int(board.cell_H_pix * cooldown_ratio)
                if overlay_height > 0 and board.img.img is not None:
                    h, w = board.img.img.shape[:2]
                    if y + overlay_height <= h and x + board.cell_W_pix <= w:
                        overlay = board.img.img[y:y + overlay_height, x:x + board.cell_W_pix].copy()
                        yellow_overlay = np.full_like(overlay, (0, 255, 255))  # Yellow in BGR
                        alpha = 0.5
                        blended = cv2.addWeighted(yellow_overlay, alpha, overlay, 1 - alpha, 0)
                        board.img.img[y:y + overlay_height, x:x + board.cell_W_pix] = blended
        except Exception:
            pass  # Error message suppressed
