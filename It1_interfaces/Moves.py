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
                            dc, dr = map(int, coords_part.split(','))
                            self.move_deltas.append((dr, dc))  # store as (row_delta, col_delta)
                        except ValueError:
                            print(f"Warning: Could not parse move line: {line}")
                    else:
                        print(f"Warning: Invalid move format: {line}")

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
