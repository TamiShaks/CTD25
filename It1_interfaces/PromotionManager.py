"""
PromotionManager - Manages pawn promotions
Handles all logic related to promoting pawns to other pieces
"""
import pathlib
from typing import Dict, Optional, Tuple
from .PieceFactory import PieceFactory
from .Command import Command
from .Moves import Moves
import traceback

class PromotionManager:
    def __init__(self, board, pieces_root: str = "pieces"):
        """Initialize promotion manager with board reference."""
        self.board = board
        self.pieces_root = pathlib.Path(pieces_root)
        self.piece_factory = PieceFactory(board, self.pieces_root)
        
        # Mapping from promotion choice to piece type
        self.promotion_map = {
            "Q": {"Black": "QB", "White": "QW"},
            "R": {"Black": "RB", "White": "RW"}, 
            "B": {"Black": "BB", "White": "BW"},
            "N": {"Black": "NB", "White": "NW"}
        }
        
        # Default promotion for invalid choices
        self.default_promotion = {
            "Black": "QB",
            "White": "QW"
        }
    
    def get_promotion_piece_type(self, old_piece, promotion_choice: str) -> str:
        """Get the new piece type based on promotion choice and piece color."""
        try:
            return self.promotion_map[promotion_choice][old_piece.color]
        except KeyError:
            return self.default_promotion[old_piece.color]

    def copy_piece_state(self, old_piece, new_piece) -> None:
        """Copy state and attributes from old piece to new piece."""
        # Copy basic attributes
        new_piece.color = old_piece.color
        new_piece.move_count = getattr(old_piece, 'move_count', 0)
        new_piece.has_moved = getattr(old_piece, 'has_moved', False)
        new_piece.last_action_time = getattr(old_piece, 'last_action_time', 0)
        
        # Copy position and movement state
        physics = new_piece.current_state.physics
        old_physics = old_piece.current_state.physics
        physics.current_cell = old_physics.current_cell
        physics.target_cell = old_physics.target_cell
        physics.is_moving = old_physics.is_moving

    def load_piece_moves(self, piece, piece_type: str) -> bool:
        """Load movement rules for the new piece type."""
        moves_file = self.pieces_root / piece_type / "moves.txt"
        if not moves_file.exists():
            print(f"Warning: No moves file found for {piece_type}")
            return False
            
        piece.current_state.moves = Moves(moves_file, (self.board.H_cells, self.board.W_cells))
        return True

    def handle_promotion(self, cmd: Command, pieces_dict: Dict, input_manager, get_time_func) -> Optional[str]:
        """Handle pawn promotion command - replace the piece with a new one."""
        if cmd.piece_id not in pieces_dict:
            return None
            
        try:
            old_piece = pieces_dict[cmd.piece_id]
            target_pos = cmd.params[1]
            promotion_choice = cmd.params[2]
            
            # Get new piece type and create piece
            new_piece_type = self.get_promotion_piece_type(old_piece, promotion_choice)
            new_piece_id = new_piece_type + old_piece.piece_id[2:]
            
            print(f"PROMOTION: {old_piece.piece_id} to {new_piece_id} at {target_pos}")
            
            # Get current state
            current_pos = old_piece.current_state.physics.current_cell
            current_state_name = getattr(old_piece.current_state, 'state', 'idle')
            
            # Create and configure new piece
            new_piece = self.piece_factory.create_piece(new_piece_type, current_pos)
            if not new_piece:
                print(f"Failed to create new piece of type {new_piece_type}")
                return None
                
            # Set up new piece
            new_piece.piece_id = new_piece_id
            new_piece.piece_type = promotion_choice
            self.copy_piece_state(old_piece, new_piece)
            
            # Load movement rules
            if not self.load_piece_moves(new_piece, new_piece_type):
                return None
                
            # Update game state
            del pieces_dict[old_piece.piece_id]
            pieces_dict[new_piece_id] = new_piece
            
            # Update selections
            for player in ['A', 'B']:
                if (hasattr(input_manager, 'selection') and 
                    input_manager.selection[player]['selected'] == old_piece):
                    input_manager.selection[player]['selected'] = new_piece
                    print(f"Updated {player} selection to new piece {new_piece_id}")
            
            print(f"Successfully created and replaced with new {new_piece_type} piece")
            return new_piece_id
                
        except Exception as e:
            print(f"Error during promotion: {e}")
            traceback.print_exc()
            return None
