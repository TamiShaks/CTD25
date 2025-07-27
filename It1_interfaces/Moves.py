import pathlib
from typing import List, Tuple

class Moves:
    """
    A class to manage move patterns for game pieces, based on a text file.

    The move definitions are parsed from a text file, and stored as (dr, dc) tuples
    which represent vertical and horizontal deltas from a current board position.
    """

    def __init__(self, txt_path: pathlib.Path, dims: Tuple[int, int]):
        """
        Initialize the Moves object.

        Args:
            txt_path (pathlib.Path): Path to the text file containing move definitions.
            dims (Tuple[int, int]): Board dimensions as (height, width).
        """
        self.board_height, self.board_width = dims
        self.move_deltas: List[Tuple[int, int]] = []

        if txt_path.exists():
            with open(txt_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue  # Skip comments and empty lines

                    if ':' in line:
                        # Format like "1,0:non_capture"
                        coords_part = line.split(':')[0].strip()
                    else:
                        coords_part = line.strip()

                    if ',' in coords_part:
                        try:
                            dr, dc = map(int, coords_part.split(','))  # Fixed: row,col not col,row!
                            self.move_deltas.append((dr, dc))  # store as (row_delta, col_delta)
                        except ValueError:
                            continue  # Skip invalid format lines


    def get_moves(self, r: int, c: int) -> List[Tuple[int, int]]:
        """
        Calculate all valid moves from the given position (r, c).

        Args:
            r (int): Current row position.
            c (int): Current column position.

        Returns:
            List[Tuple[int, int]]: List of valid target cells after applying move deltas.
        """
        valid_moves = []


        for dr, dc in self.move_deltas:
            new_r = r + dr
            new_c = c + dc
            if 0 <= new_r < self.board_height and 0 <= new_c < self.board_width:
                valid_moves.append((new_r, new_c))

        return valid_moves

    def is_path_blocked(self, start_pos, end_pos, piece_type, all_pieces):
        """Check if the path from start_pos to end_pos is blocked by other pieces."""
        # Knights can jump over other pieces
        if piece_type == "N":
            return False
        
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        
        # Calculate direction of movement
        row_dir = 0 if start_row == end_row else (1 if end_row > start_row else -1)
        col_dir = 0 if start_col == end_col else (1 if end_col > start_col else -1)
        
        # Check each square along the path (excluding start and end)
        current_row = start_row + row_dir
        current_col = start_col + col_dir
        
        while (current_row, current_col) != (end_row, end_col):
            # Check if there's a piece at this position
            for piece in all_pieces.values():
                piece_pos = tuple(piece.current_state.physics.current_cell)
                if piece_pos == (current_row, current_col):
                    return True
            
            # Move to next position along the path
            current_row += row_dir
            current_col += col_dir
        
        return False
