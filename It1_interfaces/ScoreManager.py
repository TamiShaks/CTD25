from It1_interfaces.EventTypes import MOVE_DONE, PIECE_CAPTURED

class ScoreManager:
    def __init__(self):
        self.score = {"White": 0, "Black": 0}
        self.piece_values = {
            "P": 1,  # Pawn
            "R": 5,  # Rook
            "N": 3,  # Knight
            "B": 3,  # Bishop
            "Q": 9,  # Queen
            "K": 100  # King (game-ending value)
        }
        self.moves_count = {"White": 0, "Black": 0}
    
    def update(self, event_type, data):
        if event_type == PIECE_CAPTURED:
            piece = data.get("piece")
            if piece and hasattr(piece, "color") and hasattr(piece, "piece_type"):
                # Award points to the opposing player (who captured the piece)
                captured_color = piece.color
                capturing_color = "Black" if captured_color == "White" else "White"
                piece_value = self.piece_values.get(piece.piece_type, 1)
                
                self.score[capturing_color] += piece_value
                
        elif event_type == MOVE_DONE:
            command = data.get("command")
            if command and hasattr(command, "piece_id"):
                # Try to determine the color from piece_id or find the piece
                piece_id = command.piece_id
                if "W" in piece_id:
                    self.moves_count["White"] += 1
                elif "B" in piece_id:
                    self.moves_count["Black"] += 1
    
    def get_score(self):
        """Get current scores."""
        return self.score.copy()
    
    def get_moves_count(self):
        """Get move counts."""
        return self.moves_count.copy()
    
    def display_scoreboard(self):
        """Display current game statistics."""
        print("=" * 50)
        print("🏆 SCOREBOARD 🏆")
        print(f"White: {self.score['White']} points ({self.moves_count['White']} moves)")
        print(f"Black: {self.score['Black']} points ({self.moves_count['Black']} moves)")
        print("=" * 50)
