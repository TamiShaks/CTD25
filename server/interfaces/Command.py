
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class Command:
    timestamp: int
    piece_id: str
    type: str
    params: List
    
    def __post_init__(self):
        if not isinstance(self.params, list):
            self.params = []
    
    @classmethod
    def create_move_command(cls, timestamp: int, piece_id: str, 
                          start_position: Tuple[int, int], 
                          end_position: Tuple[int, int]) -> "Command":
        return cls(timestamp, piece_id, "Move", [start_position, end_position])
    
    @classmethod 
    def create_jump_command(cls, timestamp: int, piece_id: str,
                          start_position: Tuple[int, int], 
                          landing_position: Tuple[int, int]) -> "Command":
        return cls(timestamp, piece_id, "Jump", [start_position, landing_position])
    
    @classmethod
    def create_idle_command(cls, timestamp: int, piece_id: str) -> "Command":
        return cls(timestamp, piece_id, "idle", [])
    
    @classmethod
    def create_promotion_command(cls, timestamp: int, piece_id: str,
                               start_position: Tuple[int, int], 
                               promotion_position: Tuple[int, int],
                               selected_piece_type: str) -> "Command":
        return cls(timestamp, piece_id, "Promotion", 
                  [start_position, promotion_position, selected_piece_type])
    
    def get_source_cell(self) -> Optional[Tuple[int, int]]:
        return (self.params[0] 
                if self.params and isinstance(self.params[0], tuple) 
                else None)
    
    def get_target_cell(self) -> Optional[Tuple[int, int]]:
        return (self.params[1] 
                if len(self.params) >= 2 and isinstance(self.params[1], tuple)
                else None)
