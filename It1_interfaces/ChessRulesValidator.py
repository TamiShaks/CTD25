class ChessRulesValidator:
    """Validator for chess-specific movement rules."""
    
    def __init__(self):
        """Initialize the chess rules validator."""
        pass
    
    def is_valid_move(self, piece, start_pos, target_pos, target_piece, all_pieces):
        """
        Check if a move is valid according to chess rules.
        
        Args:
            piece: The piece attempting to move
            start_pos: Starting position tuple (row, col)
            target_pos: Target position tuple (row, col) 
            target_piece: Piece at target position (if any)
            all_pieces: Dictionary of all pieces for path checking
            
        Returns:
            bool: True if move is valid, False otherwise
        """
        # Check friendly fire
        if target_piece and hasattr(target_piece, 'color') and hasattr(piece, 'color'):
            if target_piece.color == piece.color:
                return False  # Can't capture own pieces
        
        # Check piece-specific rules
        if piece.piece_type == "P":
            return self._is_valid_pawn_move(piece, start_pos, target_pos, target_piece)
        
        # Check path blocking for pieces that can't jump
        if piece.current_state.moves.is_path_blocked(start_pos, target_pos, piece.piece_type, all_pieces):
            return False
            
        return True
    
    def is_pawn_promotion(self, piece, target_pos):
        """
        Check if a pawn move results in promotion.
        
        Args:
            piece: The pawn piece
            target_pos: Target position tuple (row, col)
            
        Returns:
            bool: True if this move promotes the pawn
        """
        if piece.piece_type != "P":
            return False
            
        # White pawns promote when reaching row 0 (top of board)
        if piece.color == "White" and target_pos[0] == 0:
            return True
            
        # Black pawns promote when reaching row 7 (bottom of board) 
        if piece.color == "Black" and target_pos[0] == 7:
            return True
            
        return False
    
    def _is_valid_pawn_move(self, pawn, start_pos, target_pos, target_piece):
        """Check if pawn move is valid according to chess rules."""
        if pawn.piece_type != "P":
            return True  # Not a pawn, allow move
        
        row_diff = target_pos[0] - start_pos[0]
        col_diff = abs(target_pos[1] - start_pos[1])
        
        # Determine direction based on color
        if pawn.color == "White":
            expected_direction = -1  # White moves up (decreasing rows)
        else:
            expected_direction = 1   # Black moves down (increasing rows)
        
        # Allow only diagonal capture
        if target_piece:
            return col_diff == 1 and row_diff == expected_direction
        
        # Forward movement (no capture)
        if col_diff == 0:
            if row_diff == expected_direction:
                return True  # Single step forward
            elif row_diff == 2 * expected_direction and not pawn.has_moved:
                return True  # Double step on first move
        
        return False
