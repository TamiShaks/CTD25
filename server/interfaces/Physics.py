from typing import Tuple, Optional
from Command import Command
from Board import Board
import time

class Physics:
    """Manages piece movement physics and position calculations."""
    
    MOVEMENT_SPEED_CELLS_PER_SECOND = 4.0

    def __init__(self, starting_board_cell: Tuple[int, int], game_board: "Board", movement_speed: float = 1.0):
        self.starting_board_cell = starting_board_cell
        self.current_board_cell = starting_board_cell
        self.target_board_cell = starting_board_cell
        self.game_board = game_board
        self.movement_speed = movement_speed
        self.is_currently_moving = False
        self.movement_start_time = 0
        self.movement_duration_ms = 0
        
    def create_independent_copy(self) -> "Physics":
        independent_physics = Physics(self.starting_board_cell, self.game_board, self.movement_speed)
        independent_physics.current_board_cell = self.current_board_cell
        independent_physics.target_board_cell = self.target_board_cell
        independent_physics.is_currently_moving = self.is_currently_moving
        independent_physics.movement_start_time = self.movement_start_time
        independent_physics.movement_duration_ms = self.movement_duration_ms
        return independent_physics
        
    def execute_command_physics(self, command: Command):
        if self.is_movement_command(command):
            self.start_movement_to_target(command)
        elif self.is_jump_command(command):
            self.start_jump_animation(command)
        else:
            self.stop_any_current_movement()
    
    def is_movement_command(self, command: Command) -> bool:
        return command.type == "Move" and command.params
    
    def is_jump_command(self, command: Command) -> bool:
        return command.type == "Jump" and command.params
    
    def start_movement_to_target(self, command: Command):
        self.target_board_cell = command.params[1]
        self.is_currently_moving = True
        self.movement_start_time = command.timestamp
        self.movement_duration_ms = self.calculate_movement_duration()
    
    def start_jump_animation(self, command: Command):
        self.target_board_cell = self.current_board_cell  # Jump in place
        self.is_currently_moving = True
        self.movement_start_time = command.timestamp
        self.movement_duration_ms = 1500  # 1.5 seconds for jump animation
    
    def stop_any_current_movement(self):
        self.is_currently_moving = False
    
    def calculate_movement_duration(self) -> int:
        distance_in_rows = abs(self.target_board_cell[0] - self.current_board_cell[0])
        distance_in_cols = abs(self.target_board_cell[1] - self.current_board_cell[1])
        max_distance = max(distance_in_rows, distance_in_cols)
        duration_ms = int(max_distance / self.MOVEMENT_SPEED_CELLS_PER_SECOND * 1000)
        return duration_ms

    def update_movement_state(self, current_time_ms: int) -> bool:
        if not self.is_currently_moving:
            return False
            
        elapsed_time = current_time_ms - self.movement_start_time

        if elapsed_time >= self.movement_duration_ms:
            self.current_board_cell = self.target_board_cell
            self.is_currently_moving = False
            return True  # Movement just completed
        
        return False  # Movement still in progress

    def can_piece_be_captured(self) -> bool:
        return not self.is_currently_moving

    def can_piece_capture_others(self) -> bool:
        return not self.is_currently_moving

    def get_current_pixel_position(self, current_time_ms: int = None) -> Tuple[int, int]:
        if self.is_currently_moving and self.movement_duration_ms > 0:
            if current_time_ms is None:
                current_time_ms = int(time.time() * 1000)
            
            elapsed_time = current_time_ms - self.movement_start_time
            elapsed_time = max(0, min(self.movement_duration_ms, elapsed_time))
            movement_progress = elapsed_time / self.movement_duration_ms if self.movement_duration_ms > 0 else 1.0

            start_pixel_x = self.current_board_cell[1] * self.game_board.cell_W_pix
            start_pixel_y = self.current_board_cell[0] * self.game_board.cell_H_pix
            target_pixel_x = self.target_board_cell[1] * self.game_board.cell_W_pix
            target_pixel_y = self.target_board_cell[0] * self.game_board.cell_H_pix

            interpolated_x = int(start_pixel_x + (target_pixel_x - start_pixel_x) * movement_progress)
            interpolated_y = int(start_pixel_y + (target_pixel_y - start_pixel_y) * movement_progress)

            return (interpolated_x, interpolated_y)
        else:
            stationary_x = self.current_board_cell[1] * self.game_board.cell_W_pix
            stationary_y = self.current_board_cell[0] * self.game_board.cell_H_pix
            return (stationary_x, stationary_y)
    
    # Legacy aliases for backward compatibility
    def copy(self):
        return self.create_independent_copy()
    
    def reset(self, command):
        return self.execute_command_physics(command)
    
    def update(self, current_time_ms):
        return self.update_movement_state(current_time_ms)
    
    def get_pos(self, current_time_ms=None):
        return self.get_current_pixel_position(current_time_ms)
    
    def can_be_captured(self):
        return self.can_piece_be_captured()
    
    def can_capture(self):
        return self.can_piece_capture_others()
    
    # Legacy property aliases
    @property
    def start_cell(self):
        return self.starting_board_cell
    
    @start_cell.setter
    def start_cell(self, value):
        self.starting_board_cell = value
    
    @property
    def current_cell(self):
        return self.current_board_cell
    
    @current_cell.setter
    def current_cell(self, value):
        self.current_board_cell = value
    
    @property
    def target_cell(self):
        return self.target_board_cell
    
    @target_cell.setter
    def target_cell(self, value):
        self.target_board_cell = value
    
    @property
    def board(self):
        return self.game_board
    
    @board.setter
    def board(self, value):
        self.game_board = value
    
    @property
    def is_moving(self):
        return self.is_currently_moving
    
    @is_moving.setter
    def is_moving(self, value):
        self.is_currently_moving = value
    
    @property
    def move_start_time(self):
        return self.movement_start_time
    
    @move_start_time.setter
    def move_start_time(self, value):
        self.movement_start_time = value
    
    @property
    def move_duration(self):
        return self.movement_duration_ms
    
    @move_duration.setter
    def move_duration(self, value):
        self.movement_duration_ms = value
