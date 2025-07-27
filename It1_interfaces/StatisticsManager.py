import time
from typing import Dict, List


class StatisticsManager:
    """Manager for displaying game statistics and piece counts."""
    
    def __init__(self):
        """Initialize the statistics manager."""
        pass
    
    def display_final_statistics(self, pieces: Dict, start_time: float):
        """Display final game statistics from all managers."""
        print("\n" + "="*60)
        print("🎮 FINAL GAME STATISTICS 🎮")
        print("="*60)
        
        game_duration = time.time() - start_time
        print(f"⏱️  Game Duration: {game_duration:.1f} seconds")
        print(f"🎯 Total Pieces Remaining: {len(pieces)}")
        
        # Count pieces by color and type
        self.print_piece_counts(pieces)
        print("="*60)

    def display_live_statistics(self, pieces: Dict, start_time: float):
        """Display live game statistics during gameplay."""
        print("\n" + "="*50)
        print("📊 LIVE GAME STATISTICS 📊")
        print("="*50)
        
        game_duration = time.time() - start_time
        print(f"⏱️  Game Time: {game_duration:.1f}s")
        
        # Count pieces and states
        self.print_live_counts(pieces)
        print("="*50)
        print("Press TAB again for updated stats, ESC to quit")

    def _count_pieces_by_color(self, pieces: Dict):
        """Helper function to count pieces by color."""
        white_pieces = len([p for p in pieces.values() if hasattr(p, 'color') and p.color == "White"])
        black_pieces = len([p for p in pieces.values() if hasattr(p, 'color') and p.color == "Black"])
        return white_pieces, black_pieces
    
    def print_piece_counts(self, pieces: Dict):
        """Print piece counts by color and type."""
        white_pieces, black_pieces = self._count_pieces_by_color(pieces)
        
        print(f"⚪ White Pieces: {white_pieces}")
        print(f"⚫ Black Pieces: {black_pieces}")
        
        # Count by type
        piece_counts = {}
        for piece in pieces.values():
            if hasattr(piece, 'piece_type'):
                piece_type = piece.piece_type
                if piece_type not in piece_counts:
                    piece_counts[piece_type] = {"White": 0, "Black": 0}
                if hasattr(piece, 'color'):
                    piece_counts[piece_type][piece.color] += 1
        
        print("\n📊 Remaining Pieces by Type:")
        piece_names = {"P": "Pawns", "R": "Rooks", "N": "Knights", "B": "Bishops", "Q": "Queens", "K": "Kings"}
        for piece_type, counts in piece_counts.items():
            name = piece_names.get(piece_type, f"Type {piece_type}")
            print(f"   {name}: White {counts['White']}, Black {counts['Black']}")

    def print_live_counts(self, pieces: Dict):
        """Print live piece and state counts."""
        white_pieces, black_pieces = self._count_pieces_by_color(pieces)
        
        print(f"⚪ White Pieces: {white_pieces}")
        print(f"⚫ Black Pieces: {black_pieces}")
        
        # Count kings and states
        kings = [p for p in pieces.values() if p.piece_type == "K"]
        white_kings = len([k for k in kings if k.color == "White"])
        black_kings = len([k for k in kings if k.color == "Black"])
        
        moving_pieces = len([p for p in pieces.values() if p.current_state.physics.is_moving])
        idle_pieces = len([p for p in pieces.values() if p.current_state.state == "idle"])
        
        print(f"👑 Kings: White {white_kings}, Black {black_kings}")
        print(f"🏃 Moving Pieces: {moving_pieces}")
        print(f"💤 Idle Pieces: {idle_pieces}")
