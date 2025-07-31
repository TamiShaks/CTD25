import pathlib
from typing import List, Tuple

class PieceMovementRules:
    """Manages valid movement patterns for chess pieces from configuration files."""

    def __init__(self, movement_file_path: pathlib.Path, board_dimensions: Tuple[int, int]):
        self.board_height, self.board_width = board_dimensions
        self.movement_deltas: List[Tuple[int, int]] = []
        self.load_movement_patterns_from_file(movement_file_path)

    def load_movement_patterns_from_file(self, file_path: pathlib.Path):
        if not file_path.exists():
            return
            
        with open(file_path, 'r') as movement_file:
            for line in movement_file:
                movement_delta = self.parse_movement_line(line.strip())
                if movement_delta:
                    self.movement_deltas.append(movement_delta)

    def parse_movement_line(self, line: str) -> Tuple[int, int] | None:
        if not line or line.startswith('#'):
            return None
            
        coordinates_text = line.split(':')[0].strip() if ':' in line else line.strip()
        
        if ',' not in coordinates_text:
            return None
            
        try:
            row_delta, col_delta = map(int, coordinates_text.split(','))
            return (row_delta, col_delta)
        except ValueError:
            return None


    def calculate_valid_moves_from_position(self, current_row: int, current_col: int) -> List[Tuple[int, int]]:
        valid_target_positions = []
        
        for row_delta, col_delta in self.movement_deltas:
            target_row = current_row + row_delta
            target_col = current_col + col_delta
            
            if self.is_position_within_board_bounds(target_row, target_col):
                valid_target_positions.append((target_row, target_col))
        
        return valid_target_positions

    def is_position_within_board_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.board_height and 0 <= col < self.board_width

    def is_movement_path_blocked_by_pieces(self, start_position, target_position, piece_type, all_game_pieces):
        if self.can_piece_type_jump_over_obstacles(piece_type):
            return False
        
        path_squares = self.calculate_path_squares_between_positions(start_position, target_position)
        return self.any_square_occupied_by_piece(path_squares, all_game_pieces)

    def can_piece_type_jump_over_obstacles(self, piece_type: str) -> bool:
        return piece_type == "N"  # Knights can jump over other pieces

    def calculate_path_squares_between_positions(self, start_pos, end_pos) -> List[Tuple[int, int]]:
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        
        movement_direction = self.calculate_movement_direction(start_pos, end_pos)
        path_squares = []
        
        current_row, current_col = start_row + movement_direction[0], start_col + movement_direction[1]
        
        while (current_row, current_col) != (end_row, end_col):
            path_squares.append((current_row, current_col))
            current_row += movement_direction[0]
            current_col += movement_direction[1]
        
        return path_squares

    def calculate_movement_direction(self, start_pos, end_pos) -> Tuple[int, int]:
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        
        row_direction = 0 if start_row == end_row else (1 if end_row > start_row else -1)
        col_direction = 0 if start_col == end_col else (1 if end_col > start_col else -1)
        
        return (row_direction, col_direction)

    def any_square_occupied_by_piece(self, squares_to_check, all_game_pieces) -> bool:
        occupied_positions = {tuple(piece.current_state.physics.current_board_cell) for piece in all_game_pieces.values()}
        return any(square in occupied_positions for square in squares_to_check)
    
    # Legacy aliases for backward compatibility
    def get_moves(self, r: int, c: int) -> List[Tuple[int, int]]:
        return self.calculate_valid_moves_from_position(r, c)
    
    def is_path_blocked(self, start_pos, end_pos, piece_type, all_pieces):
        return self.is_movement_path_blocked_by_pieces(start_pos, end_pos, piece_type, all_pieces)
    
    @property
    def move_deltas(self):
        return self.movement_deltas

# Legacy class alias
Moves = PieceMovementRules
