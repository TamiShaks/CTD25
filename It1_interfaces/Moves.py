# # Moves.py  – drop-in replacement
# import pathlib
# from typing import List, Tuple

# class Moves:
   
#     def __init__(self, txt_path: pathlib.Path, dims: Tuple[int, int]):
#         """Initialize moves with rules from text file and board dimensions."""
#         pass

#     def get_moves(self, r: int, c: int) -> List[Tuple[int, int]]:
#         """Get all possible moves from a given position."""
#         pass

# Moves.py – drop-in replacement
import pathlib
from typing import List, Tuple

class Moves:
    def __init__(self, txt_path: pathlib.Path, dims: Tuple[int, int]):
        """Initialize moves with rules from text file and board dimensions."""
        self.board_height, self.board_width = dims
        self.move_deltas: List[Tuple[int, int]] = []
        
        if txt_path.exists():
            with open(txt_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and ',' in line:
                        try:
                            dc, dr = map(int, line.split(','))
                            self.move_deltas.append((dr, dc))
                        except ValueError:
                            continue

    def get_moves(self, r: int, c: int) -> List[Tuple[int, int]]:
        """Get all possible moves from a given position."""
        valid_moves = []
        
        for dr, dc in self.move_deltas:
            new_r = r + dr
            new_c = c + dc
            
            # Check bounds
            if 0 <= new_r < self.board_height and 0 <= new_c < self.board_width:
                valid_moves.append((new_r, new_c))
        
        return valid_moves