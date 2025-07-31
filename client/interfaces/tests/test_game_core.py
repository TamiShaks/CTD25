"""
Simplified test suite for Game class focusing on core logic.

Tests the main game functionality without complex GUI mocking:
- Win condition detection  
- Collision detection and capture resolution
- Input processing
- Game state management
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os
import time
import queue

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import required classes
from Command import Command
from EventTypes import GAME_STARTED, GAME_ENDED, MOVE_DONE, PIECE_CAPTURED


class TestGameCore(unittest.TestCase):
    """Test suite for Game class core functionality."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock all external dependencies to focus on core logic
        with patch('It1_interfaces.Game.pygame'), \
             patch('It1_interfaces.Game.cv2'), \
             patch('It1_interfaces.Game.StatisticsManager'), \
             patch('It1_interfaces.Game.ThreadedInputManager'), \
             patch('It1_interfaces.Game.GameUI'):
            
            from Game import Game
            self.Game = Game
            
            # Create mock pieces and board
            self.mock_pieces_list, self.mock_pieces_dict = self._create_mock_pieces()
            self.mock_board = self._create_mock_board()

    def _create_mock_pieces(self):
        """Create mock pieces for testing."""
        pieces_list = []
        pieces_dict = {}
        
        # Create white king
        white_king = Mock()
        white_king.piece_id = "KW1"
        white_king.piece_type = "K"
        white_king.color = "White"
        white_king.current_state.physics.current_cell = (7, 4)
        white_king.current_state.physics.is_moving = False
        white_king.current_state.state = "idle"
        pieces_list.append(white_king)
        pieces_dict["KW1"] = white_king
        
        # Create black king
        black_king = Mock()
        black_king.piece_id = "KB1"
        black_king.piece_type = "K"
        black_king.color = "Black"
        black_king.current_state.physics.current_cell = (0, 4)
        black_king.current_state.physics.is_moving = False
        black_king.current_state.state = "idle"
        pieces_list.append(black_king)
        pieces_dict["KB1"] = black_king
        
        # Create white pawn
        white_pawn = Mock()
        white_pawn.piece_id = "PW1"
        white_pawn.piece_type = "P"
        white_pawn.color = "White"
        white_pawn.current_state.physics.current_cell = (6, 0)
        white_pawn.current_state.physics.is_moving = False
        white_pawn.current_state.state = "idle"
        pieces_list.append(white_pawn)
        pieces_dict["PW1"] = white_pawn
        
        return pieces_list, pieces_dict

    def _create_mock_board(self):
        """Create mock board for testing."""
        board = Mock()
        board.cell_W_pix = 64
        board.cell_H_pix = 64
        board.W_cells = 8
        board.H_cells = 8
        board.clone.return_value = board
        board.img = Mock()
        return board

    def test_game_initialization_basic(self):
        """Test Game class basic initialization."""
        game = self.Game(self.mock_pieces_list, self.mock_board)
        
        # Verify game attributes
        self.assertIsNotNone(game.board)
        self.assertIsNotNone(game.pieces)
        self.assertIsInstance(game.user_input_queue, queue.Queue)
        self.assertFalse(game._should_quit)
        self.assertEqual(len(game.pieces), 3)  # 3 mock pieces

    def test_game_time_calculation(self):
        """Test game time calculation."""
        with patch('It1_interfaces.Game.time.time', return_value=1000.0):
            game = self.Game(self.mock_pieces_list, self.mock_board)
        
        # Test time calculation with different current time
        with patch('It1_interfaces.Game.time.time', return_value=1005.5):
            result = game.game_time_ms()
            self.assertEqual(result, 5500)  # (1005.5 - 1000.0) * 1000

    def test_clone_board_functionality(self):
        """Test board cloning."""
        game = self.Game(self.mock_pieces_list, self.mock_board)
        
        result = game.clone_board()
        
        self.mock_board.clone.assert_called_once()
        self.assertEqual(result, self.mock_board)

    def test_process_input_valid_piece(self):
        """Test processing input for valid piece."""
        game = self.Game(self.mock_pieces_list, self.mock_board)
        
        cmd = Command(
            timestamp=1000,
            piece_id="KW1",
            type="move",
            params=[(7, 5)]
        )
        
        game._process_input(cmd)
        
        # Verify piece.on_command was called
        game.pieces["KW1"].on_command.assert_called_once()

    def test_process_input_invalid_piece(self):
        """Test processing input for non-existent piece."""
        game = self.Game(self.mock_pieces_list, self.mock_board)
        
        cmd = Command(
            timestamp=1000,
            piece_id="INVALID",
            type="move",
            params=[(3, 3)]
        )
        
        # Should not raise exception
        game._process_input(cmd)

    def test_win_condition_one_king_remaining(self):
        """Test win detection when one king remains."""
        game = self.Game(self.mock_pieces_list, self.mock_board)
        
        # Remove black king
        del game.pieces["KB1"]
        
        result = game._is_win()
        self.assertTrue(result)

    def test_win_condition_both_kings_present(self):
        """Test no win when both kings are present."""
        game = self.Game(self.mock_pieces_list, self.mock_board)
        
        result = game._is_win()
        self.assertFalse(result)

    def test_win_condition_no_kings(self):
        """Test win detection when no kings remain."""
        game = self.Game(self.mock_pieces_list, self.mock_board)
        
        # Remove both kings
        del game.pieces["KB1"]
        del game.pieces["KW1"]
        
        result = game._is_win()
        self.assertTrue(result)

    def test_collision_resolution_no_collision(self):
        """Test collision resolution when pieces are separate."""
        game = self.Game(self.mock_pieces_list, self.mock_board)
        
        # Set pieces at different positions
        game.pieces["KW1"].current_state.physics.get_pos.return_value = (7, 4)
        game.pieces["KB1"].current_state.physics.get_pos.return_value = (0, 4)
        game.pieces["PW1"].current_state.physics.get_pos.return_value = (6, 0)
        
        initial_piece_count = len(game.pieces)
        
        game._resolve_collisions()
        
        # No pieces should be removed
        self.assertEqual(len(game.pieces), initial_piece_count)

    def test_collision_resolution_enemy_capture(self):
        """Test collision resolution with enemy capture."""
        game = self.Game(self.mock_pieces_list, self.mock_board)
        
        # Set white and black pieces at same position
        collision_pos = (4, 4)
        game.pieces["KW1"].current_state.physics.get_pos.return_value = collision_pos
        game.pieces["KB1"].current_state.physics.get_pos.return_value = collision_pos
        game.pieces["PW1"].current_state.physics.get_pos.return_value = (6, 0)
        
        # Set white king as moving (attacker)
        game.pieces["KW1"].current_state.physics.is_moving = True
        game.pieces["KB1"].current_state.physics.is_moving = False
        
        game._resolve_collisions()
        
        # Black king should be captured
        self.assertNotIn("KB1", game.pieces)
        self.assertIn("KW1", game.pieces)

    def test_friendly_collision_handling(self):
        """Test handling of friendly collision."""
        game = self.Game(self.mock_pieces_list, self.mock_board)
        
        # Create two same-color pieces
        stationary_piece = Mock()
        stationary_piece.current_state.physics.is_moving = False
        stationary_piece.current_state.state = "idle"
        
        moving_piece = Mock()
        moving_piece.current_state.physics.is_moving = True
        moving_piece.current_state.state = "move"
        moving_piece.piece_id = "test_piece"
        
        pieces = [stationary_piece, moving_piece]
        
        with patch.object(game, '_block_piece_movement') as mock_block:
            game._handle_friendly_collision(pieces)
            
            # Moving piece should be blocked
            mock_block.assert_called_once_with(moving_piece)

    def test_piece_movement_blocking(self):
        """Test blocking a piece's movement."""
        game = self.Game(self.mock_pieces_list, self.mock_board)
        
        piece = Mock()
        piece.piece_id = "test_piece"
        piece.current_state.physics.current_cell = (3, 3)
        
        game._block_piece_movement(piece)
        
        # Verify piece physics are reset
        self.assertEqual(piece.current_state.physics.target_cell, (3, 3))
        self.assertFalse(piece.current_state.physics.is_moving)
        piece.on_command.assert_called_once()

    def test_enemy_collision_handling(self):
        """Test handling of enemy collision."""
        game = self.Game(self.mock_pieces_list, self.mock_board)
        
        # Create attacking and defending pieces
        attacking_piece = Mock()
        attacking_piece.current_state.physics.is_moving = True
        attacking_piece.current_state.state = "move"
        
        defending_piece = Mock()
        defending_piece.current_state.physics.is_moving = False
        defending_piece.current_state.state = "idle"
        
        pieces_in_cell = [attacking_piece, defending_piece]
        to_remove = []
        
        game._handle_enemy_collision(pieces_in_cell, to_remove)
        
        # Defending piece should be marked for removal
        self.assertIn(defending_piece, to_remove)
        self.assertNotIn(attacking_piece, to_remove)

    def test_game_with_event_bus(self):
        """Test game initialization with event bus."""
        mock_event_bus = Mock()
        
        game = self.Game(self.mock_pieces_list, self.mock_board, event_bus=mock_event_bus)
        
        self.assertEqual(game.event_bus, mock_event_bus)

    def test_game_with_custom_managers(self):
        """Test game initialization with custom managers."""
        mock_score_manager = Mock()
        mock_move_logger = Mock()
        
        game = self.Game(self.mock_pieces_list, self.mock_board, 
                        score_manager=mock_score_manager, move_logger=mock_move_logger)
        
        self.assertEqual(game.score_manager, mock_score_manager)
        self.assertEqual(game.move_logger, mock_move_logger)


if __name__ == '__main__':
    unittest.main()
