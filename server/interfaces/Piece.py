from Board import Board
from Command import Command
from State import State
import cv2
import numpy as np

class PieceMovementTracker:
    """Tracks movement history for pieces like pawns with special first-move rules."""
    
    def __init__(self):
        self.move_count = 0
        self.has_moved = False
    
    def record_movement(self):
        self.move_count += 1
        self.has_moved = True
    
    def reset(self):
        self.move_count = 0
        self.has_moved = False

class PieceCooldownSystem:
    """Manages action cooldowns to prevent spam movements."""
    
    def __init__(self, cooldown_duration_ms: int = 2000):
        self.last_action_time = 0
        self.cooldown_duration_ms = cooldown_duration_ms
    
    def is_action_allowed(self, current_time_ms: int) -> bool:
        return (current_time_ms - self.last_action_time) >= self.cooldown_duration_ms
    
    def record_action(self, action_time_ms: int):
        self.last_action_time = action_time_ms
    
    def get_remaining_cooldown(self, current_time_ms: int) -> int:
        remaining = self.cooldown_duration_ms - (current_time_ms - self.last_action_time)
        return max(0, remaining)
    
    def reset(self, reset_time_ms: int):
        self.last_action_time = reset_time_ms

class Piece:
    """A chess piece with state machine, movement tracking, and cooldown system."""
    
    def __init__(self, piece_id: str, initial_state: State, piece_type: str):
        self.piece_id = piece_id
        self.current_state = initial_state
        self.piece_type = piece_type
        self.start_time = 0
        
        self.color = self.extract_color_from_piece_id(piece_id)
        self.movement_tracker = PieceMovementTracker()
        self.cooldown_system = PieceCooldownSystem()

    def extract_color_from_piece_id(self, piece_id: str) -> str:
        if len(piece_id) < 2:
            return "Unknown"
        color_code = piece_id[1]
        return "White" if color_code == 'W' else "Black" if color_code == 'B' else "Unknown"

    def handle_command(self, command: Command, current_time_ms: int):
        if not self.is_command_for_this_piece(command):
            return
        
        if self.should_block_command(command, current_time_ms):
            return
        
        if self.is_invalid_pawn_double_move(command):
            return
        
        self.process_valid_command(command, current_time_ms)

    def is_command_for_this_piece(self, command: Command) -> bool:
        return command.piece_id == self.piece_id

    def should_block_command(self, command: Command, current_time_ms: int) -> bool:
        if self.is_piece_resting() and self.is_movement_command(command):
            return True
        return not self.cooldown_system.is_action_allowed(current_time_ms)

    def is_piece_resting(self) -> bool:
        return self.current_state.state == "long_rest"

    def is_movement_command(self, command: Command) -> bool:
        return command.type in ["Move", "Jump"]

    def is_invalid_pawn_double_move(self, command: Command) -> bool:
        if self.piece_type != "P" or command.type != "Move":
            return False
        
        move_distance = self.calculate_move_distance(command)
        return move_distance == 2 and self.movement_tracker.has_moved

    def calculate_move_distance(self, command: Command) -> int:
        source = command.get_source_cell()
        target = command.get_target_cell()
        if not source or not target:
            return 0
        return abs(target[0] - source[0])

    def process_valid_command(self, command: Command, current_time_ms: int):
        previous_state_name = self.current_state.state
        new_state = self.current_state.get_state_after_command(command, current_time_ms)
        
        if new_state != self.current_state:
            self.current_state = new_state
            self.cooldown_system.record_action(current_time_ms)
            
            if self.is_movement_command(command):
                self.movement_tracker.record_movement()
        
        self.current_state.physics.execute_command_physics(command)

    def reset_piece_to_initial_state(self, reset_time_ms: int):
        self.start_time = reset_time_ms
        self.cooldown_system.reset(reset_time_ms)
        self.movement_tracker.reset()
        
        idle_command = Command.create_idle_command(reset_time_ms, self.piece_id)
        self.current_state.reset(idle_command)

    def update_piece_state(self, current_time_ms: int):
        updated_state = self.current_state.update(current_time_ms)
        if updated_state != self.current_state:
            self.current_state = updated_state

    def render_piece_on_board(self, board: Board, current_time_ms: int):
        sprite = self.get_current_sprite(current_time_ms)
        piece_position = self.get_current_position(current_time_ms)
        
        try:
            sprite.draw_on(board.img, piece_position[0], piece_position[1])
            self.draw_cooldown_overlay_if_needed(board, piece_position, current_time_ms)
        except Exception:
            pass

    def get_current_sprite(self, current_time_ms: int):
        return self.current_state.graphics.get_img(
            state_start_time=self.current_state.state_start_time,
            rest_duration_ms=self.current_state.rest_duration_ms,
            now_ms=current_time_ms
        )

    def get_current_position(self, current_time_ms: int) -> tuple:
        return self.current_state.physics.get_current_pixel_position(current_time_ms)

    def draw_cooldown_overlay_if_needed(self, board: Board, piece_position: tuple, current_time_ms: int):
        remaining_cooldown = self.cooldown_system.get_remaining_cooldown(current_time_ms)
        if remaining_cooldown <= 0:
            return
        
        cooldown_ratio = remaining_cooldown / self.cooldown_system.cooldown_duration_ms
        overlay_height = int(board.cell_H_pix * cooldown_ratio)
        
        if overlay_height > 0 and board.img.img is not None:
            self.apply_yellow_cooldown_overlay(board, piece_position, overlay_height)

    def apply_yellow_cooldown_overlay(self, board: Board, piece_position: tuple, overlay_height: int):
        x, y = piece_position
        board_height, board_width = board.img.img.shape[:2]
        
        if y + overlay_height <= board_height and x + board.cell_W_pix <= board_width:
            overlay_region = board.img.img[y:y + overlay_height, x:x + board.cell_W_pix].copy()
            yellow_overlay = np.full_like(overlay_region, (0, 255, 255))
            blended_overlay = cv2.addWeighted(yellow_overlay, 0.5, overlay_region, 0.5, 0)
            board.img.img[y:y + overlay_height, x:x + board.cell_W_pix] = blended_overlay
