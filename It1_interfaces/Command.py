# from dataclasses import dataclass, field
# from typing import List, Dict, Tuple, Optional

# @dataclass
# class Command:
#     timestamp: int          # ms since game start
#     piece_id: str
#     type: str               # "Move" | "Jump" | …
#     params: List            # payload (e.g. ["e2", "e4"]) 

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

@dataclass
class Command:
    timestamp: int          # ms since game start
    piece_id: str
    type: str               # "Move" | "Jump" | "Attack" | "idle" | "complete"
    params: List            # payload (e.g. ["e2", "e4"] or [(row1,col1), (row2,col2)])
    
    def __post_init__(self):
        """Validate command after initialization."""
        if not isinstance(self.params, list):
            self.params = []
    
    @classmethod
    def create_move_command(cls, timestamp: int, piece_id: str, 
                           from_cell: Tuple[int, int], to_cell: Tuple[int, int]) -> "Command":
        """Factory method for creating move commands."""
        return cls(
            timestamp=timestamp,
            piece_id=piece_id,
            type="Move",
            params=[from_cell, to_cell]
        )
    
    @classmethod
    def create_jump_command(cls, timestamp: int, piece_id: str, 
                           from_cell: Tuple[int, int], to_cell: Tuple[int, int]) -> "Command":
        """Factory method for creating jump commands."""
        return cls(
            timestamp=timestamp,
            piece_id=piece_id,
            type="Jump",
            params=[from_cell, to_cell]
        )
    
    @classmethod
    def create_idle_command(cls, timestamp: int, piece_id: str) -> "Command":
        """Factory method for creating idle commands."""
        return cls(
            timestamp=timestamp,
            piece_id=piece_id,
            type="idle",
            params=[]
        )
    
    def get_source_cell(self) -> Optional[Tuple[int, int]]:
        """Get the source cell from move parameters."""
        if len(self.params) >= 1 and isinstance(self.params[0], tuple):
            return self.params[0]
        return None
    
    def get_target_cell(self) -> Optional[Tuple[int, int]]:
        """Get the target cell from move parameters."""
        if len(self.params) >= 2 and isinstance(self.params[1], tuple):
            return self.params[1]
        return None
    
    def __str__(self) -> str:
        """String representation of the command."""
        return f"Command({self.type}, {self.piece_id}, {self.params})"