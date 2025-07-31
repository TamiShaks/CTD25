#!/usr/bin/env python3
"""Game Movement History Tracker - Records and displays recent player moves."""
import time
from typing import Dict, List, Optional, Tuple


class GameMovementHistoryTracker:
    """Tracks and displays recent moves for both players with timestamps."""
    
    def __init__(self, maximum_moves_to_remember: int = 6):
        self.player_move_histories = {"A": [], "B": []}
        self.maximum_moves_to_remember = maximum_moves_to_remember
        self.game_start_time = time.time()
    
    def process_game_event(self, event_type: str, event_data: Dict):
        if event_type == "MOVE_DONE":
            self.record_move_from_event_data(event_data.get("command"))

    def record_move_from_event_data(self, movement_command):
        if not self.is_valid_movement_command(movement_command):
            return
        
        player_identifier = self.extract_player_from_piece_id(movement_command.piece_id)
        if player_identifier:
            formatted_move_text = self.create_formatted_move_description(movement_command)
            self.add_move_to_player_history(player_identifier, formatted_move_text)

    def is_valid_movement_command(self, command) -> bool:
        return command and hasattr(command, 'piece_id') and len(command.piece_id) >= 2

    def extract_player_from_piece_id(self, piece_id: str) -> Optional[str]:
        color_mapping = {"W": "A", "B": "B"}
        return color_mapping.get(piece_id[1])

    def create_formatted_move_description(self, command) -> str:
        current_timestamp = time.strftime("%H:%M:%S")
        
        if self.command_has_position_parameters(command):
            return f"[{current_timestamp}] {command.piece_id}: {command.params[0]} → {command.params[1]}"
        else:
            return f"[{current_timestamp}] {command.piece_id}: {command.type}"

    def command_has_position_parameters(self, command) -> bool:
        return (hasattr(command, 'params') and command.params and len(command.params) >= 2 and 
                isinstance(command.params[0], tuple) and isinstance(command.params[1], tuple))

    def add_move_to_player_history(self, player_identifier: str, move_description: str):
        self.player_move_histories[player_identifier].append(move_description)
        self.maintain_history_size_limit(player_identifier)

    def maintain_history_size_limit(self, player_identifier: str):
        history = self.player_move_histories[player_identifier]
        while len(history) > self.maximum_moves_to_remember:
            history.pop(0)

    def record_move_from_console_output(self, console_text_line: str):
        parsed_move_data = self.parse_console_move_line(console_text_line)
        if parsed_move_data:
            player_identifier, move_description = parsed_move_data
            self.add_move_to_player_history(player_identifier, move_description)

    def parse_console_move_line(self, line: str) -> Optional[Tuple[str, str]]:
        if not self.is_console_move_line(line):
            return None
            
        try:
            player_identifier = "A" if "Player A:" in line else "B"
            move_text = line.split(": ", 1)[1]
            current_timestamp = time.strftime("%H:%M:%S")
            formatted_move = f"[{current_timestamp}] {move_text}"
            return (player_identifier, formatted_move)
        except (IndexError, ValueError):
            return None

    def is_console_move_line(self, line: str) -> bool:
        return "Player A:" in line or "Player B:" in line

    def get_recent_moves_for_player(self, player_identifier: str) -> List[str]:
        return self.player_move_histories.get(player_identifier, [])

    def count_moves_for_player(self, player_identifier: str) -> int:
        return len(self.player_move_histories.get(player_identifier, []))

    def reset_all_move_histories(self):
        self.player_move_histories = {"A": [], "B": []}
        self.game_start_time = time.time()
    
    # Legacy aliases for backward compatibility
    def update(self, event_type: str, data: Dict):
        return self.process_game_event(event_type, data)
    
    def handle_event(self, event_type: str, data: Dict):
        return self.process_game_event(event_type, data)
    
    def log_move_from_console(self, console_line: str):
        return self.record_move_from_console_output(console_line)
    
    def get_move_count(self, player: str) -> int:
        return self.count_moves_for_player(player)
    
    def clear_history(self):
        return self.reset_all_move_histories()
    
    # Legacy property aliases
    @property
    def player_moves(self):
        return self.player_move_histories
    
    @property
    def max_moves(self):
        return self.maximum_moves_to_remember
    
    @property
    def start_time(self):
        return self.game_start_time

# Legacy class alias
MoveLogger = GameMovementHistoryTracker
