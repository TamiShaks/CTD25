"""
PromotionManager - מנהל קידומי חיילים
מטפל בכל הלוגיקה של קידום חייל רגלי לחיילים אחרים
"""
import pathlib
from typing import Dict
from .PieceFactory import PieceFactory
from .Command import Command


class PromotionManager:
    def __init__(self, board, pieces_root="pieces"):
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
    
    def promote_piece(self, old_piece, promotion_choice: str, target_pos: tuple) -> tuple:
        """
        Promote a piece to a new type.
        Returns: (new_piece, new_piece_id) or (None, None) if failed
        """
        try:
            # Get new piece type
            new_piece_type = self.promotion_map[promotion_choice][old_piece.color]
            new_piece_id = new_piece_type + old_piece.piece_id[2:]  # Keep the number part
            
            print(f"🎉 PROMOTION: {old_piece.piece_id} → {new_piece_id} at {target_pos}")
            
            # Save current state
            current_pos = old_piece.current_state.physics.current_cell
            current_target = old_piece.current_state.physics.target_cell
            is_moving = old_piece.current_state.physics.is_moving
            current_state_name = getattr(old_piece.current_state, 'state', 'idle')
            
            # Create new piece
            new_piece = self.piece_factory.create_piece(new_piece_type, current_pos)
            
            if new_piece:
                # Update piece properties
                new_piece.piece_id = new_piece_id
                new_piece.piece_type = promotion_choice  # CRITICAL: Update piece type!
                new_piece.color = old_piece.color
                new_piece.move_count = getattr(old_piece, 'move_count', 0)
                new_piece.has_moved = getattr(old_piece, 'has_moved', False)
                new_piece.last_action_time = getattr(old_piece, 'last_action_time', 0)
                
                # Set position and movement state
                new_piece.current_state.physics.current_cell = current_pos
                new_piece.current_state.physics.target_cell = current_target
                new_piece.current_state.physics.is_moving = is_moving
                
                # CRITICAL: Ensure moves are correctly loaded for the new piece type
                from .Moves import Moves
                moves_file = self.pieces_root / new_piece_type / "moves.txt"
                if moves_file.exists():
                    new_piece.current_state.moves = Moves(moves_file, (self.board.H_cells, self.board.W_cells))
                    print(f"🎯 Updated moves for {new_piece_type} from {moves_file}")
                    print(f"🔍 DEBUG: Piece type now: {new_piece.piece_type}, was: P")
                else:
                    print(f"⚠️ Warning: No moves file found for {new_piece_type}")
                
                print(f"✅ Successfully created new {new_piece_type} piece")
                return new_piece, new_piece_id
            else:
                print(f"❌ Failed to create new piece of type {new_piece_type}")
                return None, None
                
        except Exception as e:
            print(f"❌ Error during promotion: {e}")
            import traceback
            traceback.print_exc()
            return None, None
