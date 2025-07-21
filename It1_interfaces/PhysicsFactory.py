# from Board import Board
# from Physics import Physics


# class PhysicsFactory:      # very light for now
#     def __init__(self, board: Board): 
#         """Initialize physics factory with board."""
#         pass
        
#     def create(self, start_cell, cfg) -> Physics:
#         """Create a physics object with the given configuration."""
#         pass 

# PhysicsFactory.py

from Board import Board
from Physics import Physics

class PhysicsFactory:
    def __init__(self, board: Board): 
        """Initialize physics factory with board."""
        self.board = board
        
    def create(self, start_cell, cfg) -> Physics:
        """Create a physics object with the given configuration."""
        speed = cfg.get('speed', 1.0)
        return Physics(start_cell, self.board, speed)