"""
Pawn Promotion System - Manages pawn promotions to other pieces
"""
import pathlib
from typing import Dict, Optional, Tuple, Any
from PieceFactory import PieceFactory
from Command import Command
from Moves import Moves
import traceback


class PromotionResult:
    """Container for promotion operation results."""
    
    def __init__(self, success: bool, new_piece_id: Optional[str] = None, 
                 error_message: Optional[str] = None):
        self.success = success
        self.new_piece_id = new_piece_id
        self.error_message = error_message


class PawnPromotionManager:
    """Manages pawn promotions - replacing pawns with chosen pieces."""
    
    # Available promotion choices
    VALID_PROMOTION_CHOICES = {"Q", "R", "B", "N"}
    
    # Mapping from promotion choice to actual piece types by color
    DEFAULT_PROMOTION_MAP = {
        "Q": {"Black": "QB", "White": "QW"},
        "R": {"Black": "RB", "White": "RW"},
        "B": {"Black": "BB", "White": "BW"},
        "N": {"Black": "NB", "White": "NW"}
    }
    
    # Fallback promotions if choice is invalid
    DEFAULT_PROMOTION_FALLBACK = {
        "Black": "QB",
        "White": "QW"
    }
    
    def __init__(self, board, pieces_root: str = "pieces", debug: bool = False):
        """Initialize promotion manager with board reference."""
        self.board = board
        self.pieces_root = pathlib.Path(pieces_root)
        self.piece_factory = PieceFactory(board, self.pieces_root)
        self.debug = debug
        
        # Use default mapping (can be customized later)
        self.promotion_map = self.DEFAULT_PROMOTION_MAP.copy()
        self.default_promotion = self.DEFAULT_PROMOTION_FALLBACK.copy()
    
    def set_custom_promotion_mapping(self, custom_map: Dict[str, Dict[str, str]]):
        """Set a custom promotion mapping."""
        self.promotion_map = custom_map
    
    def get_promotion_piece_type(self, old_piece, promotion_choice: str) -> str:
        """Get the new piece type based on promotion choice and piece color."""
        try:
            return self.promotion_map[promotion_choice][old_piece.color]
        except KeyError:
            if self.debug:
                print(f"Invalid promotion choice '{promotion_choice}', using default")
            return self.default_promotion[old_piece.color]

    def _validate_promotion_request(self, cmd: Command, pieces_dict: Dict) -> Tuple[bool, str]:
        """Validate promotion request parameters."""
        if cmd.piece_id not in pieces_dict:
            return False, f"Piece {cmd.piece_id} not found in game"
            
        if len(cmd.params) < 3:
            return False, "Invalid promotion command - missing parameters"
            
        promotion_choice = cmd.params[2]
        if promotion_choice not in self.VALID_PROMOTION_CHOICES:
            return False, f"Invalid promotion choice: {promotion_choice}"
            
        old_piece = pieces_dict[cmd.piece_id]
        if not hasattr(old_piece, 'color'):
            return False, f"Piece {cmd.piece_id} missing color attribute"
            
        return True, ""

    def _copy_basic_attributes(self, old_piece, new_piece):
        """Copy basic piece attributes from old to new piece."""
        new_piece.color = old_piece.color
        new_piece.move_count = getattr(old_piece, 'move_count', 0)
        new_piece.movement_tracker.has_moved = old_piece.movement_tracker.has_moved
        new_piece.last_action_time = getattr(old_piece, 'last_action_time', 0)

    def _copy_physics_state(self, old_piece, new_piece):
        """Copy physics and position state from old to new piece."""
        if not (hasattr(old_piece, 'current_state') and hasattr(new_piece, 'current_state')):
            return
            
        old_physics = old_piece.current_state.physics
        new_physics = new_piece.current_state.physics
        
        new_physics.current_cell = old_physics.current_cell
        new_physics.target_cell = old_physics.target_cell
        new_physics.is_moving = old_physics.is_moving

    def copy_piece_state(self, old_piece, new_piece) -> None:
        """Copy state and attributes from old piece to new piece."""
        self._copy_basic_attributes(old_piece, new_piece)
        self._copy_physics_state(old_piece, new_piece)

    def load_piece_moves(self, piece, piece_type: str) -> bool:
        """Load movement rules for the new piece type."""
        moves_file = self.pieces_root / piece_type / "moves.txt"
        
        if not moves_file.exists():
            if self.debug:
                print(f"Warning: No moves file found for {piece_type}")
            return False
            
        try:
            piece.current_state.moves = Moves(moves_file, (self.board.H_cells, self.board.W_cells))
            return True
        except Exception as e:
            if self.debug:
                print(f"Error loading moves for {piece_type}: {e}")
            return False

    def _create_new_piece(self, old_piece, promotion_choice: str) -> Tuple[Optional[Any], str]:
        """Create the new promoted piece."""
        new_piece_type = self.get_promotion_piece_type(old_piece, promotion_choice)
        new_piece_id = new_piece_type + old_piece.piece_id[2:]
        
        current_pos = old_piece.current_state.physics.current_cell
        new_piece = self.piece_factory.create_piece(new_piece_type, current_pos)
        
        if not new_piece:
            return None, f"Failed to create new piece of type {new_piece_type}"
            
        # Configure new piece
        new_piece.piece_id = new_piece_id
        
        return new_piece, new_piece_id

    def _update_game_state(self, pieces_dict: Dict, old_piece, new_piece, new_piece_id: str):
        """Update the game pieces dictionary."""
        del pieces_dict[old_piece.piece_id]
        pieces_dict[new_piece_id] = new_piece

    def _update_player_selections(self, input_manager, old_piece, new_piece, new_piece_id: str):
        """Update player selections if they had the old piece selected."""
        if not hasattr(input_manager, 'selection'):
            return
            
        for player in ['A', 'B']:
            if input_manager.selection[player]['selected'] == old_piece:
                input_manager.selection[player]['selected'] = new_piece
                if self.debug:
                    print(f"Updated {player} selection to new piece {new_piece_id}")

    def handle_promotion(self, cmd: Command, pieces_dict: Dict, input_manager, get_time_func) -> PromotionResult:
        """Handle pawn promotion command - replace the piece with a new one."""
        # Validate request
        is_valid, error_msg = self._validate_promotion_request(cmd, pieces_dict)
        if not is_valid:
            return PromotionResult(False, error_message=error_msg)
            
        try:
            old_piece = pieces_dict[cmd.piece_id]
            promotion_choice = cmd.params[2]
            
            if self.debug:
                print(f"PROMOTION: {old_piece.piece_id} to {promotion_choice} at {cmd.params[1]}")
            
            # Create new piece
            new_piece, new_piece_id = self._create_new_piece(old_piece, promotion_choice)
            if not new_piece:
                return PromotionResult(False, error_message=new_piece_id)  # new_piece_id contains error msg
                
            # Set up new piece
            self.copy_piece_state(old_piece, new_piece)
            
            # Load movement rules
            if not self.load_piece_moves(new_piece, new_piece_id[:2]):
                return PromotionResult(False, error_message=f"Failed to load moves for {new_piece_id}")
                
            # Update game state
            self._update_game_state(pieces_dict, old_piece, new_piece, new_piece_id)
            self._update_player_selections(input_manager, old_piece, new_piece, new_piece_id)
            
            if self.debug:
                print(f"Successfully promoted to {new_piece_id}")
                
            return PromotionResult(True, new_piece_id)
                
        except Exception as e:
            error_msg = f"Error during promotion: {e}"
            if self.debug:
                print(error_msg)
                traceback.print_exc()
            return PromotionResult(False, error_message=error_msg)

    def get_available_promotions(self, piece_color: str) -> Dict[str, str]:
        """Get available promotion options for a piece color."""
        result = {}
        for choice in self.VALID_PROMOTION_CHOICES:
            if choice in self.promotion_map and piece_color in self.promotion_map[choice]:
                result[choice] = self.promotion_map[choice][piece_color]
        return result

    def is_valid_promotion_choice(self, choice: str) -> bool:
        """Check if a promotion choice is valid."""
        return choice in self.VALID_PROMOTION_CHOICES

    def get_promotion_statistics(self) -> Dict[str, Any]:
        """Get statistics about promotion configuration."""
        return {
            "valid_choices": list(self.VALID_PROMOTION_CHOICES),
            "mapping_count": len(self.promotion_map),
            "debug_enabled": self.debug,
            "pieces_root": str(self.pieces_root)
        }


# Backward compatibility alias
PromotionManager = PawnPromotionManager
