import time
from typing import Dict, List, Tuple
from collections import defaultdict


class StatisticsManager:
    """Manager for displaying game statistics and piece counts."""
    
    def __init__(self):
        """Initialize the statistics manager."""
        self.piece_names = {
            "P": "Pawns", "R": "Rooks", "N": "Knights", 
            "B": "Bishops", "Q": "Queens", "K": "Kings"
        }
    
    def display_final_statistics(self, pieces: Dict, start_time: float):
        """Display final game statistics from all managers."""
        self._print_header("FINAL GAME STATISTICS", 60)
        
        game_duration = time.time() - start_time
        print(f"  Game Duration: {game_duration:.1f} seconds")
        print(f" Total Pieces Remaining: {len(pieces)}")
        
        self.print_piece_counts(pieces)
        print("="*60)

    def display_live_statistics(self, pieces: Dict, start_time: float):
        """Display live game statistics during gameplay."""
        self._print_header("LIVE GAME STATISTICS", 50)
        
        game_duration = time.time() - start_time
        print(f"  Game Time: {game_duration:.1f}s")
        
        self.print_live_counts(pieces)
        print("="*50)
        print("Press TAB again for updated stats, ESC to quit")

    def _print_header(self, title: str, width: int):
        """Print a formatted header."""
        print("\n" + "="*width)
        print(f" {title} ")
        print("="*width)

    def _count_pieces_by_color(self, pieces: Dict) -> Tuple[int, int]:
        """Helper function to count pieces by color."""
        white_pieces = sum(1 for p in pieces.values() 
                          if hasattr(p, 'color') and p.color == "White")
        black_pieces = sum(1 for p in pieces.values() 
                          if hasattr(p, 'color') and p.color == "Black")
        return white_pieces, black_pieces

    def _count_pieces_by_type(self, pieces: Dict) -> Dict:
        """Count pieces by type and color."""
        piece_counts = defaultdict(lambda: {"White": 0, "Black": 0})
        
        for piece in pieces.values():
            if hasattr(piece, 'piece_type') and hasattr(piece, 'color'):
                piece_counts[piece.piece_type][piece.color] += 1
        
        return dict(piece_counts)
    
    def print_piece_counts(self, pieces: Dict):
        """Print piece counts by color and type."""
        white_pieces, black_pieces = self._count_pieces_by_color(pieces)
        
        print(f" White Pieces: {white_pieces}")
        print(f" Black Pieces: {black_pieces}")
        
        piece_counts = self._count_pieces_by_type(pieces)
        
        print("\n Remaining Pieces by Type:")
        for piece_type, counts in piece_counts.items():
            name = self.piece_names.get(piece_type, f"Type {piece_type}")
            print(f"   {name}: White {counts['White']}, Black {counts['Black']}")

    def print_live_counts(self, pieces: Dict):
        """Print live piece and state counts."""
        white_pieces, black_pieces = self._count_pieces_by_color(pieces)
        
        print(f" White Pieces: {white_pieces}")
        print(f" Black Pieces: {black_pieces}")
        
        self._print_kings_count(pieces)
        self._print_movement_stats(pieces)
        self._print_state_breakdown(pieces)
        print(" Controls: TAB=stats, ESC=quit")

    def _print_kings_count(self, pieces: Dict):
        """Print king counts by color."""
        kings = [p for p in pieces.values() if hasattr(p, 'piece_type') and p.piece_type == "K"]
        white_kings = sum(1 for k in kings if hasattr(k, 'color') and k.color == "White")
        black_kings = sum(1 for k in kings if hasattr(k, 'color') and k.color == "Black")
        print(f" Kings: White {white_kings}, Black {black_kings}")

    def _print_movement_stats(self, pieces: Dict):
        """Print movement statistics."""
        moving_pieces = sum(1 for p in pieces.values() 
                           if hasattr(p, 'current_state') and p.current_state.physics.is_moving)
        idle_pieces = sum(1 for p in pieces.values() 
                         if hasattr(p, 'current_state') and p.current_state.state == "idle")
        
        print(f" Moving Pieces: {moving_pieces}")
        print(f" Idle Pieces: {idle_pieces}")

    def _print_state_breakdown(self, pieces: Dict):
        """Print state breakdown for all pieces."""
        state_counts = defaultdict(int)
        
        for piece in pieces.values():
            if hasattr(piece, 'current_state'):
                state_counts[piece.current_state.state] += 1
        
        print(" States: ", end="")
        for state, count in state_counts.items():
            print(f"{state}:{count} ", end="")
        print()  # New line
