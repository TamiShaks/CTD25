#!/usr/bin/env python3
"""
 ScoreManager Compact
"""
from It1_interfaces.EventTypes import MOVE_DONE, PIECE_CAPTURED


class ScoreManager:
    """Compact score management"""
    
    def __init__(self):
        self.scores = {"White": 0, "Black": 0}
        self.moves = {"White": 0, "Black": 0}
        self.values = {"P": 1, "R": 5, "N": 3, "B": 3, "Q": 9, "K": 100}
    
    def update(self, event_type, data):
        """Update from event"""
        if event_type == PIECE_CAPTURED:
            self._handle_capture(data.get("piece"))
        elif event_type == MOVE_DONE:
            self._handle_move(data.get("command"))
    
    def _handle_capture(self, piece):
        """Handle capture"""
        if not piece or not hasattr(piece, "color") or not hasattr(piece, "piece_type"):
            return
        
        # Points to opposing player
        enemy_color = "Black" if piece.color == "White" else "White"
        points = self.values.get(piece.piece_type, 1)
        self.scores[enemy_color] += points
    
    def _handle_move(self, cmd):
        """Handle move"""
        if not cmd or not hasattr(cmd, "piece_id"):
            return
        
        # Count moves
        if "W" in cmd.piece_id:
            self.moves["White"] += 1
        elif "B" in cmd.piece_id:
            self.moves["Black"] += 1
    
    def get_player_score(self, player):
        """Player score (A=White, B=Black)"""
        color = "White" if player == "A" else "Black"
        return self.scores.get(color, 0)
    
    def get_score(self):
        """All scores"""
        return self.scores.copy()
