"""
Chess Rules Validation - Validates chess movements and game mechanics
"""


class ChessGameRulesValidator:
    """Validates chess movements according to official rules."""
    
    def __init__(self):
        pass

    def is_valid_move(self, piece, start_pos, target_pos, target_piece, all_pieces):
        """Validate a chess move according to all applicable rules."""
        # Prevent friendly fire
        if target_piece and hasattr(target_piece, 'color') and hasattr(piece, 'color'):
            if target_piece.color == piece.color:
                return False
        
        # Apply piece-specific movement rules
        if piece.piece_type.startswith("P"):
            return self._validate_pawn_movement(piece, start_pos, target_pos, target_piece)
        
        # Check path obstruction for non-jumping pieces
        if piece.current_state.moves.is_path_blocked(start_pos, target_pos, piece.piece_type, all_pieces):
            return False
            
        return True

    def detect_pawn_promotion_opportunity(self, piece, target_pos):
        """Detect if a pawn move triggers promotion."""
        # Only pawns can be promoted
        if not piece.piece_type.startswith("P"):
            return False
            
        # White pawns promote when reaching row 0 (top of board)
        if piece.color == "White" and target_pos[0] == 0:
            return True
            
        # Black pawns promote when reaching row 7 (bottom of board) 
        if piece.color == "Black" and target_pos[0] == 7:
            return True
            
        return False

    def _validate_pawn_movement(self, pawn, start_pos, target_pos, target_piece):
        """Validate pawn movement according to chess rules."""
        if not pawn.piece_type.startswith("P"):
            return True
        
        row_diff = target_pos[0] - start_pos[0]
        col_diff = abs(target_pos[1] - start_pos[1])
        
        expected_direction = -1 if pawn.color == "White" else 1
        
        # Diagonal capture
        if target_piece:
            return col_diff == 1 and row_diff == expected_direction
        
        # Forward movement
        if col_diff == 0:
            if row_diff == expected_direction:
                return True
            elif row_diff == 2 * expected_direction and not pawn.movement_tracker.has_moved:
                return True
        
        return False

# Backward compatibility alias
ChessRulesValidator = ChessGameRulesValidator

# Backward compatibility for method names
ChessGameRulesValidator.is_pawn_promotion = ChessGameRulesValidator.detect_pawn_promotion_opportunity
ChessGameRulesValidator._is_valid_pawn_move = ChessGameRulesValidator._validate_pawn_movement
