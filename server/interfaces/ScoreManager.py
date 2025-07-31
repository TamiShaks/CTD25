from typing import Dict, Optional, List, Tuple
from EventTypes import MOVE_DONE, PIECE_CAPTURED
import time


class ScoreManager:
    """Manages game scoring, move counting, and statistics tracking."""
    
    # Standard chess piece values
    DEFAULT_PIECE_VALUES = {
        "P": 1,   # Pawn
        "R": 5,   # Rook  
        "N": 3,   # Knight
        "B": 3,   # Bishop
        "Q": 9,   # Queen
        "K": 100  # King (game-ending value)
    }
    
    # Color mappings
    PLAYER_COLOR_MAP = {"A": "White", "B": "Black"}
    
    def __init__(self, custom_piece_values: Optional[Dict[str, int]] = None):
        """Initialize the score manager with optional custom piece values."""
        self.piece_values = custom_piece_values or self.DEFAULT_PIECE_VALUES.copy()
        self.score = {"White": 0, "Black": 0}
        self.moves_count = {"White": 0, "Black": 0}
        self.captured_pieces = {"White": [], "Black": []}  # Track captured pieces
        self.game_start_time = time.time()
        
    def update(self, event_type, data):
        """Handle game events and update scores accordingly."""
        if event_type == PIECE_CAPTURED:
            self._handle_piece_captured(data)
        elif event_type == MOVE_DONE:
            self._handle_move_done(data)
    
    def _handle_piece_captured(self, data: Dict):
        """Handle piece capture events."""
        piece = data.get("piece")
        if not self._is_valid_piece(piece):
            return
            
        captured_color = piece.color
        capturing_color = self._get_opposing_color(captured_color)
        piece_value = self.piece_values.get(piece.piece_type, 1)
        
        # Update score
        self.score[capturing_color] += piece_value
        
        # Track captured piece
        self.captured_pieces[capturing_color].append({
            "type": piece.piece_type,
            "value": piece_value,
            "timestamp": time.time()
        })
    
    def _handle_move_done(self, data: Dict):
        """Handle move completion events."""
        command = data.get("command")
        if not command or not hasattr(command, "piece_id"):
            return
            
        color = self._extract_color_from_piece_id(command.piece_id)
        if color:
            self.moves_count[color] += 1
    
    def _is_valid_piece(self, piece) -> bool:
        """Check if piece has required attributes."""
        return (piece and 
                hasattr(piece, "color") and 
                hasattr(piece, "piece_type") and
                piece.color in ["White", "Black"])
    
    def _get_opposing_color(self, color: str) -> str:
        """Get the opposing color."""
        return "Black" if color == "White" else "White"
    
    def _extract_color_from_piece_id(self, piece_id: str) -> Optional[str]:
        """Extract color from piece ID more reliably."""
        if not piece_id:
            return None
            
        piece_id_upper = piece_id.upper()
        if "W" in piece_id_upper:
            return "White"
        elif "B" in piece_id_upper:
            return "Black"
        return None
    
    def get_score(self) -> Dict[str, int]:
        """Get current scores."""
        return self.score.copy()
    
    def get_player_score(self, player: str) -> int:
        """Get score for a specific player (A/B format)."""
        color = self.PLAYER_COLOR_MAP.get(player, "White")
        return self.score.get(color, 0)
    
    def get_moves_count(self) -> Dict[str, int]:
        """Get move counts."""
        return self.moves_count.copy()
    
    def get_captured_pieces(self, color: str) -> List[Dict]:
        """Get list of pieces captured by a color."""
        return self.captured_pieces.get(color, []).copy()
    
    def get_total_captures(self) -> Dict[str, int]:
        """Get total number of pieces captured by each color."""
        return {
            "White": len(self.captured_pieces["White"]),
            "Black": len(self.captured_pieces["Black"])
        }
    
    def get_capture_value_breakdown(self, color: str) -> Dict[str, int]:
        """Get breakdown of captured piece values by type."""
        captured = self.captured_pieces.get(color, [])
        breakdown = {}
        
        for capture in captured:
            piece_type = capture["type"]
            breakdown[piece_type] = breakdown.get(piece_type, 0) + capture["value"]
            
        return breakdown
    
    def get_game_duration(self) -> float:
        """Get current game duration in seconds."""
        return time.time() - self.game_start_time
    
    def get_moves_per_minute(self, color: str) -> float:
        """Calculate moves per minute for a color."""
        duration_minutes = self.get_game_duration() / 60
        if duration_minutes == 0:
            return 0.0
        return self.moves_count.get(color, 0) / duration_minutes
    
    def is_winning(self, color: str) -> bool:
        """Check if a color is currently winning."""
        opposing_color = self._get_opposing_color(color)
        return self.score[color] > self.score[opposing_color]
    
    def get_score_difference(self, color: str) -> int:
        """Get score difference (positive if winning, negative if losing)."""
        opposing_color = self._get_opposing_color(color)
        return self.score[color] - self.score[opposing_color]
    
    def display_scoreboard(self):
        """Display current game statistics."""
        self._print_header()
        self._print_scores()
        self._print_moves_stats()
        self._print_captures_summary()
        self._print_footer()
    
    def _print_header(self):
        """Print scoreboard header."""
        print("=" * 60)
        print("🏆 GAME SCOREBOARD 🏆")
        print("=" * 60)
    
    def _print_scores(self):
        """Print current scores."""
        white_score = self.score["White"]
        black_score = self.score["Black"]
        
        print(f"⚪ White: {white_score} points")
        print(f"⚫ Black: {black_score} points")
        
        # Show who's winning
        if white_score > black_score:
            print(f"   → White leads by {white_score - black_score} points! 🎯")
        elif black_score > white_score:
            print(f"   → Black leads by {black_score - white_score} points! 🎯")
        else:
            print("   → Tied game! 🤝")
    
    def _print_moves_stats(self):
        """Print movement statistics."""
        duration = self.get_game_duration()
        print(f"\n📊 Game Stats (Duration: {duration:.1f}s)")
        print(f"   White: {self.moves_count['White']} moves ({self.get_moves_per_minute('White'):.1f}/min)")
        print(f"   Black: {self.moves_count['Black']} moves ({self.get_moves_per_minute('Black'):.1f}/min)")
    
    def _print_captures_summary(self):
        """Print capture summary."""
        white_captures = len(self.captured_pieces["White"])
        black_captures = len(self.captured_pieces["Black"])
        
        print(f"\n🎯 Captures:")
        print(f"   White captured: {white_captures} pieces")
        print(f"   Black captured: {black_captures} pieces")
    
    def _print_footer(self):
        """Print scoreboard footer."""
        print("=" * 60)
    
    def reset(self):
        """Reset all scores and statistics."""
        self.score = {"White": 0, "Black": 0}
        self.moves_count = {"White": 0, "Black": 0}
        self.captured_pieces = {"White": [], "Black": []}
        self.game_start_time = time.time()
