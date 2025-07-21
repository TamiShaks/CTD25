# Moves.py – Updated to handle your actual file format
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
                    if not line or line.startswith('#'):  # Skip empty lines and comments
                        continue
                    
                    # Handle different formats
                    if ':' in line:
                        # Format like "0:non_capture" or "1,1:capture"
                        coords_part = line.split(':')[0].strip()
                    else:
                        # Simple format like "1,0"
                        coords_part = line.strip()
                    
                    if ',' in coords_part:
                        try:
                            dc, dr = map(int, coords_part.split(','))
                            self.move_deltas.append((dr, dc))
                        except ValueError:
                            print(f"Warning: Could not parse move line: {line}")
                            continue
                    else:
                        print(f"Warning: Invalid move format: {line}")

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