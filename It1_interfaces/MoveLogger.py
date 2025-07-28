#!/usr/bin/env python3
"""
# MoveLogger - Game Move Recording
# Manages and displays all game moves in the user interface
"""
import time
from typing import Dict, List, Optional


class MoveLogger:
    """מחלקה לרישום moves במשחק"""
    
    def __init__(self):
        """initialization מנהל רישום המהלכים"""
        self.move_history: List[Dict] = []
        self.game_start_time = time.time()
        self.player_moves = {"A": [], "B": []}
        self.max_displayed_moves = 8
        
    def update(self, event_type: str, data: Dict):
        """Handle EventBus updates."""
        if event_type == "MOVE_DONE":
            self.handle_event(event_type, data)
    
    def handle_event(self, event_type: str, data: Dict):
        """Handle move events from the event bus."""
        if event_type == "MOVE_DONE":
            cmd = data.get("command")
            if cmd and hasattr(cmd, 'piece_id'):
                piece_id = cmd.piece_id
                # Extract player from piece ID (second character: W=A, B=B)
                if len(piece_id) >= 2:
                    color_char = piece_id[1]  # Second character is W or B
                    player = "A" if color_char == "W" else "B" if color_char == "B" else "?"
                else:
                    player = "?"
                
                if player in self.player_moves:
                    # Create move description
                    move_info = f"{piece_id}: {cmd.type}"
                    if hasattr(cmd, 'params') and cmd.params:
                        move_info += f" {cmd.params}"
                    
                    # Add to player's move list
                    self.player_moves[player].append(move_info)
                    
                    # Keep only recent moves
                    if len(self.player_moves[player]) > self.max_displayed_moves:
                        self.player_moves[player].pop(0)
                        
                    # Add to global history
                    self.move_history.append({
                        'timestamp': time.time(),
                        'player': player,
                        'piece_id': piece_id,
                        'command': cmd.type,
                        'params': getattr(cmd, 'params', [])
                    })
    
    def log_move(self, piece_id: str, from_pos: tuple, to_pos: tuple, command_type: str = "Move"):
        """Log a move manually (if needed)."""
        # Extract player from piece ID (second character: W=A, B=B)
        if len(piece_id) >= 2:
            color_char = piece_id[1]  # Second character is W or B
            player = "A" if color_char == "W" else "B" if color_char == "B" else "?"
        else:
            player = "?"
        
        move_info = f"{piece_id}: {command_type} {from_pos}→{to_pos}"
        
        if player in self.player_moves:
            self.player_moves[player].append(move_info)
            if len(self.player_moves[player]) > self.max_displayed_moves:
                self.player_moves[player].pop(0)
        
        self.move_history.append({
            'timestamp': time.time(),
            'player': player,
            'piece_id': piece_id,
            'command': command_type,
            'from_pos': from_pos,
            'to_pos': to_pos
        })
    
    def get_recent_moves_for_player(self, player: str) -> List[str]:
        """Get recent moves for a specific player."""
        return self.player_moves.get(player, [])
    
    def get_all_moves(self) -> List[str]:
        """Get all moves for display."""
        all_moves = []
        for player in ["A", "B"]:
            moves = self.get_recent_moves_for_player(player)
            all_moves.extend([f"Player {player}: {move}" for move in moves])
        return all_moves
    
    def get_move_count(self, player: str) -> int:
        """Get total move count for a player."""
        return len([move for move in self.move_history if move.get('player') == player])
    
    def get_game_duration(self) -> float:
        """Get current game duration in seconds."""
        return time.time() - self.game_start_time
    
    def clear_history(self):
        """Clear all move history."""
        self.move_history.clear()
        self.player_moves = {"A": [], "B": []}
        self.game_start_time = time.time()
