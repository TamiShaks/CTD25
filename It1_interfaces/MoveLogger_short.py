#!/usr/bin/env python3
"""
 MoveLogger Compact
"""
import time
from typing import Dict, List


class MoveLogger:
    """Compact move logging"""
    
    def __init__(self, max_moves: int = 6):
        self.player_moves = {"A": [], "B": []}
        self.max_moves = max_moves
        self.start_time = time.time()
    
    def update(self, event_type: str, data: Dict):
        """Update from event"""
        if event_type == "MOVE_DONE":
            self._log_move_from_event(data.get("command"))
    
    def handle_event(self, event_type: str, data: Dict):
        """Handle event - same as update"""
        self.update(event_type, data)
    
    def _log_move_from_event(self, cmd):
        """Log move from event"""
        if not cmd or not hasattr(cmd, 'piece_id'):
            return
        
        piece_id = cmd.piece_id
        if len(piece_id) < 2:
            return
        
        # Player identification: W=A, B=B
        player = "A" if piece_id[1] == "W" else "B" if piece_id[1] == "B" else None
        if not player:
            return
        
        # Create detailed move description with time and positions
        current_time = time.strftime("%H:%M:%S")
        
        # Check if there are position parameters in correct format
        if (hasattr(cmd, 'params') and cmd.params and len(cmd.params) >= 2 and 
            isinstance(cmd.params[0], tuple) and isinstance(cmd.params[1], tuple)):
            from_pos = cmd.params[0]
            to_pos = cmd.params[1]
            # Format similar to console: [time] piece_name: (start_position) → (end_position)
            move_text = f"[{current_time}] {piece_id}: {from_pos} → {to_pos}"
        else:
            move_text = f"[{current_time}] {piece_id}: {cmd.type}"
        
        # Add to list
        self.player_moves[player].append(move_text)
        
        # Keep maximum number of moves
        if len(self.player_moves[player]) > self.max_moves:
            self.player_moves[player].pop(0)
    
    def log_move_from_console(self, console_line: str):
        """Log move from console"""
        # Parse line like: " Player A: PW60 (6, 0) → (4, 0)"
        if "Player A:" in console_line or "Player B:" in console_line:
            try:
                # Extract data
                player = "A" if "Player A:" in console_line else "B"
                move_part = console_line.split(": ")[1]  # "PW60 (6, 0) → (4, 0)"
                
                current_time = time.strftime("%H:%M:%S")
                move_text = f"[{current_time}] {move_part}"
                
                # Add to list
                self.player_moves[player].append(move_text)
                
                # Keep maximum number of moves
                if len(self.player_moves[player]) > self.max_moves:
                    self.player_moves[player].pop(0)
            except:
                pass
    
    def get_recent_moves_for_player(self, player: str) -> List[str]:
        """Get recent moves"""
        return self.player_moves.get(player, [])
    
    def get_move_count(self, player: str) -> int:
        """Number of moves"""
        return len(self.player_moves.get(player, []))
    
    def clear_history(self):
        """Clear history"""
        self.player_moves = {"A": [], "B": []}
        self.start_time = time.time()
