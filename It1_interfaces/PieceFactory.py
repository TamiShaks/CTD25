# import pathlib
# from typing import Dict, Tuple
# import json
# from Board import Board
# from GraphicsFactory import GraphicsFactory
# from Moves import Moves
# from PhysicsFactory import PhysicsFactory
# from Piece import Piece
# from State import State


# class PieceFactory:
#     def __init__(self, board: Board, pieces_root: pathlib.Path):
#         """Initialize piece factory with board and 
#         generates the library of piece templates from the pieces directory.."""
#         pass

#     def _build_state_machine(self, piece_dir: pathlib.Path) -> State:
#         """Build a state machine for a piece from its directory."""
#         pass

#     # PieceFactory.py  – replace create_piece(...)
#     def create_piece(self, p_type: str, cell: Tuple[int, int]) -> Piece:
#         """Create a piece of the specified type at the given cell."""
#         pass 

import pathlib
from typing import Dict, Tuple
import json
from Board import Board
from GraphicsFactory import GraphicsFactory
from Moves import Moves
from PhysicsFactory import PhysicsFactory
from Piece import Piece
from State import State

class PieceFactory:
    def __init__(self, board: Board, pieces_root: pathlib.Path):
        """Initialize piece factory with board and pieces directory."""
        self.board = board
        self.pieces_root = pieces_root
        self.graphics_factory = GraphicsFactory()
        self.physics_factory = PhysicsFactory(board)
        
        # Cache of piece templates
        self.piece_templates: Dict[str, State] = {}
        
        # Build templates from pieces directory
        self._build_templates()
    
    def _build_templates(self):
        """Build piece templates from the pieces directory structure."""
        if not self.pieces_root.exists():
            print(f"Warning: Pieces directory {self.pieces_root} does not exist")
            return
            
        for piece_dir in self.pieces_root.iterdir():
            if piece_dir.is_dir():
                try:
                    template = self._build_state_machine(piece_dir)
                    self.piece_templates[piece_dir.name] = template
                except Exception as e:
                    print(f"Warning: Could not build template for {piece_dir.name}: {e}")

    def _build_state_machine(self, piece_dir: pathlib.Path) -> State:
        """Build a state machine for a piece from its directory."""
        # Load moves
        moves_file = piece_dir / "moves.txt"
        moves = Moves(moves_file, (self.board.H_cells, self.board.W_cells))
        
        # Load config if exists
        config_file = piece_dir / "config.json"
        config = {}
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)
            except:
                pass
        
        # Build states
        states_dir = piece_dir / "states"
        states = {}
        
        if states_dir.exists():
            for state_dir in states_dir.iterdir():
                if state_dir.is_dir():
                    state_name = state_dir.name
                    
                    # Load graphics
                    sprites_dir = state_dir / "sprites"
                    graphics = self.graphics_factory.load(
                        sprites_dir, 
                        config.get(state_name, {}), 
                        (self.board.cell_W_pix, self.board.cell_H_pix)
                    )
                    
                    # Create physics (will be customized per instance)
                    physics = self.physics_factory.create(
                        (0, 0), 
                        config.get(state_name, {})
                    )
                    
                    # Create state
                    state = State(moves, graphics, physics)
                    states[state_name] = state
        
        # If no states found, create a default idle state
        if not states:
            default_graphics = self.graphics_factory.load(
                piece_dir / "sprites",
                {},
                (self.board.cell_W_pix, self.board.cell_H_pix)
            )
            default_physics = self.physics_factory.create((0, 0), {})
            states["idle"] = State(moves, default_graphics, default_physics)
        
        # Set up transitions (basic state machine)
        if "idle" in states and "move" in states:
            states["idle"].set_transition("Move", states["move"])
            states["move"].set_transition("complete", states["idle"])
        
        if "idle" in states and "jump" in states:
            states["idle"].set_transition("Jump", states["jump"])
            states["jump"].set_transition("complete", states["idle"])
        
        # Return the initial state (idle by default)
        return states.get("idle", list(states.values())[0])

    def create_piece(self, p_type: str, cell: Tuple[int, int]) -> Piece:
        """Create a piece of the specified type at the given cell."""
        if p_type not in self.piece_templates:
            raise ValueError(f"Unknown piece type: {p_type}")
        
        # Clone the template state machine
        template = self.piece_templates[p_type]
        
        # Create a new state with the specific starting position
        moves = template.moves
        graphics = template.graphics.copy()
        physics = self.physics_factory.create(cell, {})
        
        initial_state = State(moves, graphics, physics)
        
        # Copy transitions if any
        initial_state.transitions = template.transitions.copy()
        
        # Generate unique piece ID
        piece_id = f"{p_type}_{cell[0]}_{cell[1]}_{id(initial_state)}"
        
        return Piece(piece_id, initial_state)