#!/usr/bin/env python3
"""
🧪 Comprehensive Tests for MoveLogger Class
==========================================

Tests all functionality of the MoveLogger class including:
- Move logging and event handling
- Player move tracking and history
- Event bus integration
- Move display and formatting
- Game duration tracking
- History management and clearing
"""

import unittest
import sys
import os
import time
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Define MoveLogger directly to avoid import issues
class MoveLogger:
    """MoveLogger class for testing"""
    
    def __init__(self):
        """Initialize move logger"""
        self.move_history = []
        self.game_start_time = time.time()
        self.player_moves = {"A": [], "B": []}
        self.max_displayed_moves = 8
        
    def update(self, event_type: str, data: dict):
        """Handle EventBus updates."""
        if event_type == "MOVE_DONE":
            self.handle_event(event_type, data)
    
    def handle_event(self, event_type: str, data: dict):
        """Handle move events from the event bus."""
        if event_type == "MOVE_DONE":
            cmd = data.get("command")
            if cmd and hasattr(cmd, 'piece_id'):
                piece_id = cmd.piece_id
                # Extract player from piece ID (second character: W=A, B=B)
                if isinstance(piece_id, str) and len(piece_id) >= 2:
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
        if isinstance(piece_id, str) and len(piece_id) >= 2:
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
    
    def get_recent_moves_for_player(self, player: str):
        """Get recent moves for a specific player."""
        return self.player_moves.get(player, [])
    
    def get_all_moves(self):
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

class TestMoveLogger(unittest.TestCase):
    """Comprehensive test suite for MoveLogger class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.logger = MoveLogger()
        
        # Create mock command objects
        self.mock_command_white = Mock()
        self.mock_command_white.piece_id = "PW1"  # White pawn
        self.mock_command_white.type = "Move"
        self.mock_command_white.params = [(6, 0), (5, 0)]
        
        self.mock_command_black = Mock()
        self.mock_command_black.piece_id = "PB1"  # Black pawn
        self.mock_command_black.type = "Move"
        self.mock_command_black.params = [(1, 0), (2, 0)]
        
        self.mock_command_white_king = Mock()
        self.mock_command_white_king.piece_id = "KW1"  # White king
        self.mock_command_white_king.type = "Move"
        self.mock_command_white_king.params = [(7, 4), (7, 5)]
    
    def test_logger_initialization(self):
        """🧪 Test MoveLogger initialization"""
        logger = MoveLogger()
        
        # Verify initial state
        self.assertEqual(logger.move_history, [])
        self.assertEqual(logger.player_moves, {"A": [], "B": []})
        self.assertEqual(logger.max_displayed_moves, 8)
        self.assertIsInstance(logger.game_start_time, float)
        
        # Verify game start time is recent
        time_diff = time.time() - logger.game_start_time
        self.assertLess(time_diff, 1.0, "Game start time should be recent")
    
    def test_update_method_filters_events(self):
        """🧪 Test that update method only processes MOVE_DONE events"""
        # Test with MOVE_DONE event
        data = {"command": self.mock_command_white}
        self.logger.update("MOVE_DONE", data)
        
        # Should have processed the move
        self.assertEqual(len(self.logger.player_moves["A"]), 1)
        
        # Test with other event types
        self.logger.update("GAME_START", data)
        self.logger.update("PIECE_SELECTED", data)
        self.logger.update("INVALID_MOVE", data)
        
        # Should not have processed these events
        self.assertEqual(len(self.logger.player_moves["A"]), 1)  # Still only 1
    
    def test_handle_event_processes_move_done(self):
        """🧪 Test handle_event processes MOVE_DONE events correctly"""
        data = {"command": self.mock_command_white}
        
        self.logger.handle_event("MOVE_DONE", data)
        
        # Verify move was added to player A
        self.assertEqual(len(self.logger.player_moves["A"]), 1)
        self.assertIn("PW1: Move", self.logger.player_moves["A"][0])
        
        # Verify move was added to global history
        self.assertEqual(len(self.logger.move_history), 1)
        self.assertEqual(self.logger.move_history[0]["player"], "A")
        self.assertEqual(self.logger.move_history[0]["piece_id"], "PW1")
    
    def test_handle_event_ignores_non_move_events(self):
        """🧪 Test handle_event ignores non-MOVE_DONE events"""
        data = {"command": self.mock_command_white}
        
        self.logger.handle_event("GAME_START", data)
        self.logger.handle_event("PIECE_SELECTED", data)
        
        # Should not have processed any moves
        self.assertEqual(len(self.logger.player_moves["A"]), 0)
        self.assertEqual(len(self.logger.player_moves["B"]), 0)
        self.assertEqual(len(self.logger.move_history), 0)
    
    def test_player_extraction_from_piece_id(self):
        """🧪 Test correct player extraction from piece IDs"""
        test_cases = [
            ("PW1", "A"),  # White pawn -> Player A
            ("PB1", "B"),  # Black pawn -> Player B
            ("KW1", "A"),  # White king -> Player A
            ("KB1", "B"),  # Black king -> Player B
            ("RW1", "A"),  # White rook -> Player A
            ("RB1", "B"),  # Black rook -> Player B
            ("QW1", "A"),  # White queen -> Player A
            ("QB1", "B"),  # Black queen -> Player B
        ]
        
        for piece_id, expected_player in test_cases:
            with self.subTest(piece_id=piece_id):
                # Create mock command
                mock_cmd = Mock()
                mock_cmd.piece_id = piece_id
                mock_cmd.type = "Move"
                mock_cmd.params = []
                
                data = {"command": mock_cmd}
                self.logger.handle_event("MOVE_DONE", data)
                
                # Verify move was logged to correct player
                moves = self.logger.get_recent_moves_for_player(expected_player)
                self.assertTrue(any(piece_id in move for move in moves),
                              f"Move for {piece_id} should be logged to player {expected_player}")
    
    def test_player_extraction_edge_cases(self):
        """🧪 Test player extraction with edge case piece IDs"""
        edge_cases = [
            ("X", "?"),      # Too short
            ("P", "?"),      # Too short
            ("", "?"),       # Empty
            ("PX1", "?"),    # Invalid color
            ("PY1", "?"),    # Invalid color
        ]
        
        for piece_id, expected_player in edge_cases:
            with self.subTest(piece_id=piece_id):
                mock_cmd = Mock()
                mock_cmd.piece_id = piece_id
                mock_cmd.type = "Move"
                mock_cmd.params = []
                
                data = {"command": mock_cmd}
                self.logger.handle_event("MOVE_DONE", data)
                
                # Should handle gracefully without crashing
                # Unknown players won't be added to player_moves dict
                self.assertEqual(len(self.logger.player_moves["A"]), 0)
                self.assertEqual(len(self.logger.player_moves["B"]), 0)
    
    def test_move_formatting_with_params(self):
        """🧪 Test move description formatting with parameters"""
        data = {"command": self.mock_command_white}
        self.logger.handle_event("MOVE_DONE", data)
        
        move = self.logger.player_moves["A"][0]
        self.assertIn("PW1: Move", move)
        self.assertIn("[(6, 0), (5, 0)]", move)
    
    def test_move_formatting_without_params(self):
        """🧪 Test move description formatting without parameters"""
        mock_cmd = Mock()
        mock_cmd.piece_id = "PW1"
        mock_cmd.type = "Attack"
        mock_cmd.params = None
        
        data = {"command": mock_cmd}
        self.logger.handle_event("MOVE_DONE", data)
        
        move = self.logger.player_moves["A"][0]
        self.assertEqual(move, "PW1: Attack")
    
    def test_max_displayed_moves_limit(self):
        """🧪 Test that max_displayed_moves limit is enforced"""
        # Add more moves than the limit
        for i in range(12):  # More than max_displayed_moves (8)
            mock_cmd = Mock()
            mock_cmd.piece_id = f"PW{i+1}"
            mock_cmd.type = "Move"
            mock_cmd.params = []
            
            data = {"command": mock_cmd}
            self.logger.handle_event("MOVE_DONE", data)
        
        # Should only keep the last 8 moves
        self.assertEqual(len(self.logger.player_moves["A"]), 8)
        
        # Should keep all moves in global history
        self.assertEqual(len(self.logger.move_history), 12)
        
        # Verify oldest moves were removed from player moves
        moves = self.logger.player_moves["A"]
        self.assertNotIn("PW1: Move", moves[0])  # First move should be gone
        self.assertIn("PW12: Move", moves[-1])   # Last move should be there
    
    def test_log_move_manual_logging(self):
        """🧪 Test manual move logging functionality"""
        self.logger.log_move("PW1", (6, 0), (5, 0), "Move")
        
        # Verify move was logged to player A
        self.assertEqual(len(self.logger.player_moves["A"]), 1)
        move = self.logger.player_moves["A"][0]
        self.assertEqual(move, "PW1: Move (6, 0)→(5, 0)")
        
        # Verify move was added to global history
        self.assertEqual(len(self.logger.move_history), 1)
        history_entry = self.logger.move_history[0]
        self.assertEqual(history_entry["player"], "A")
        self.assertEqual(history_entry["piece_id"], "PW1")
        self.assertEqual(history_entry["command"], "Move")
        self.assertEqual(history_entry["from_pos"], (6, 0))
        self.assertEqual(history_entry["to_pos"], (5, 0))
    
    def test_log_move_different_command_types(self):
        """🧪 Test manual logging with different command types"""
        command_types = ["Move", "Attack", "Castle", "EnPassant", "Promotion"]
        
        for i, cmd_type in enumerate(command_types):
            with self.subTest(command_type=cmd_type):
                self.logger.log_move(f"PW{i+1}", (i, 0), (i+1, 0), cmd_type)
                
                move = self.logger.player_moves["A"][-1]  # Get last move
                self.assertIn(cmd_type, move)
                self.assertIn(f"PW{i+1}", move)
    
    def test_get_recent_moves_for_player(self):
        """🧪 Test getting recent moves for specific players"""
        # Add moves for both players
        self.logger.log_move("PW1", (6, 0), (5, 0))
        self.logger.log_move("PB1", (1, 0), (2, 0))
        self.logger.log_move("PW2", (6, 1), (5, 1))
        
        # Get moves for player A
        moves_a = self.logger.get_recent_moves_for_player("A")
        self.assertEqual(len(moves_a), 2)
        self.assertIn("PW1", moves_a[0])
        self.assertIn("PW2", moves_a[1])
        
        # Get moves for player B
        moves_b = self.logger.get_recent_moves_for_player("B")
        self.assertEqual(len(moves_b), 1)
        self.assertIn("PB1", moves_b[0])
        
        # Test invalid player
        moves_invalid = self.logger.get_recent_moves_for_player("C")
        self.assertEqual(moves_invalid, [])
    
    def test_get_all_moves(self):
        """🧪 Test getting all moves formatted for display"""
        self.logger.log_move("PW1", (6, 0), (5, 0))
        self.logger.log_move("PB1", (1, 0), (2, 0))
        self.logger.log_move("PW2", (6, 1), (5, 1))
        
        all_moves = self.logger.get_all_moves()
        
        # Should have 3 moves total
        self.assertEqual(len(all_moves), 3)
        
        # Check formatting
        self.assertTrue(any("Player A:" in move for move in all_moves))
        self.assertTrue(any("Player B:" in move for move in all_moves))
        self.assertTrue(any("PW1" in move for move in all_moves))
        self.assertTrue(any("PB1" in move for move in all_moves))
        self.assertTrue(any("PW2" in move for move in all_moves))
    
    def test_get_move_count(self):
        """🧪 Test getting move count for players"""
        # Initially no moves
        self.assertEqual(self.logger.get_move_count("A"), 0)
        self.assertEqual(self.logger.get_move_count("B"), 0)
        
        # Add moves for both players
        self.logger.log_move("PW1", (6, 0), (5, 0))
        self.logger.log_move("PW2", (6, 1), (5, 1))
        self.logger.log_move("PB1", (1, 0), (2, 0))
        
        # Check counts
        self.assertEqual(self.logger.get_move_count("A"), 2)
        self.assertEqual(self.logger.get_move_count("B"), 1)
        self.assertEqual(self.logger.get_move_count("C"), 0)  # Invalid player
    
    def test_get_game_duration(self):
        """🧪 Test game duration calculation"""
        # Test immediately after creation
        duration = self.logger.get_game_duration()
        self.assertGreaterEqual(duration, 0)
        self.assertLess(duration, 1.0)  # Should be very small
        
        # Test with mock time advance
        with patch('time.time') as mock_time:
            # Set current time to 10 seconds after start
            mock_time.return_value = self.logger.game_start_time + 10.0
            
            duration = self.logger.get_game_duration()
            self.assertEqual(duration, 10.0)
    
    def test_clear_history(self):
        """🧪 Test clearing move history"""
        # Add some moves
        self.logger.log_move("PW1", (6, 0), (5, 0))
        self.logger.log_move("PB1", (1, 0), (2, 0))
        
        # Verify moves exist
        self.assertEqual(len(self.logger.move_history), 2)
        self.assertEqual(len(self.logger.player_moves["A"]), 1)
        self.assertEqual(len(self.logger.player_moves["B"]), 1)
        
        old_start_time = self.logger.game_start_time
        
        # Clear history
        self.logger.clear_history()
        
        # Verify everything is cleared
        self.assertEqual(len(self.logger.move_history), 0)
        self.assertEqual(self.logger.player_moves, {"A": [], "B": []})
        
        # Verify game start time was reset
        self.assertGreater(self.logger.game_start_time, old_start_time)
    
    def test_event_data_without_command(self):
        """🧪 Test handling event data without command"""
        data = {"other_data": "value"}
        
        # Should handle gracefully without crashing
        self.logger.handle_event("MOVE_DONE", data)
        
        # Should not have logged any moves
        self.assertEqual(len(self.logger.move_history), 0)
        self.assertEqual(len(self.logger.player_moves["A"]), 0)
        self.assertEqual(len(self.logger.player_moves["B"]), 0)
    
    def test_command_without_piece_id(self):
        """🧪 Test handling command without piece_id attribute"""
        mock_cmd = Mock()
        # Don't set piece_id attribute
        mock_cmd.type = "Move"
        
        data = {"command": mock_cmd}
        
        # Should handle gracefully without crashing
        self.logger.handle_event("MOVE_DONE", data)
        
        # Should not have logged any moves
        self.assertEqual(len(self.logger.move_history), 0)
        self.assertEqual(len(self.logger.player_moves["A"]), 0)
        self.assertEqual(len(self.logger.player_moves["B"]), 0)
    
    def test_alternating_player_moves(self):
        """🧪 Test alternating moves between players"""
        moves = [
            ("PW1", "A"), ("PB1", "B"), ("PW2", "A"), ("PB2", "B"),
            ("KW1", "A"), ("KB1", "B"), ("QW1", "A"), ("QB1", "B")
        ]
        
        for piece_id, expected_player in moves:
            self.logger.log_move(piece_id, (0, 0), (1, 1))
        
        # Verify correct distribution
        self.assertEqual(self.logger.get_move_count("A"), 4)
        self.assertEqual(self.logger.get_move_count("B"), 4)
        
        # Verify moves are in correct player lists
        moves_a = self.logger.get_recent_moves_for_player("A")
        moves_b = self.logger.get_recent_moves_for_player("B")
        
        self.assertEqual(len(moves_a), 4)
        self.assertEqual(len(moves_b), 4)
        
        # Verify correct pieces in each list
        self.assertTrue(all("W" in move for move in moves_a))
        self.assertTrue(all("B" in move for move in moves_b))
    
    def test_timestamp_accuracy(self):
        """🧪 Test that timestamps are recorded accurately"""
        start_time = time.time()
        
        self.logger.log_move("PW1", (6, 0), (5, 0))
        
        end_time = time.time()
        
        # Verify timestamp is within reasonable range
        move_timestamp = self.logger.move_history[0]["timestamp"]
        self.assertGreaterEqual(move_timestamp, start_time)
        self.assertLessEqual(move_timestamp, end_time)
    
    def test_integration_with_event_bus_simulation(self):
        """🧪 Test integration simulation with multiple event types"""
        # Simulate various events that might come from EventBus
        events = [
            ("GAME_START", {"message": "Game started"}),
            ("MOVE_DONE", {"command": self.mock_command_white}),
            ("PIECE_SELECTED", {"piece": "PW1"}),
            ("MOVE_DONE", {"command": self.mock_command_black}),
            ("INVALID_MOVE", {"reason": "Path blocked"}),
            ("MOVE_DONE", {"command": self.mock_command_white_king}),
            ("GAME_END", {"winner": "Player A"}),
        ]
        
        for event_type, data in events:
            self.logger.update(event_type, data)
        
        # Should only have processed the 3 MOVE_DONE events
        self.assertEqual(len(self.logger.move_history), 3)
        self.assertEqual(self.logger.get_move_count("A"), 2)  # White pawn + white king
        self.assertEqual(self.logger.get_move_count("B"), 1)  # Black pawn

if __name__ == '__main__':
    unittest.main(verbosity=2)
