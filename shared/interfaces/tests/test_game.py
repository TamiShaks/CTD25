"""
Comprehensive test suite for Game class.

Tests the main game orchestrator including:
- Game initialization and setup
- Game loop and event handling  
- Collision detection and capture resolution
- Win condition detection
- Input processing and command handling
- Drawing and rendering integration
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
import sys
import os
import time
import queue

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import from parent directory
from Game import Game
from Command import Command
from EventTypes import GAME_STARTED, GAME_ENDED, MOVE_DONE, PIECE_CAPTURED


class TestGame(unittest.TestCase):
    """Test suite for Game class covering all major functionality."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock pygame to avoid GUI dependencies
        self.pygame_patcher = patch('It1_interfaces.Game.pygame')
        self.mock_pygame = self.pygame_patcher.start()
        
        # Mock cv2 to avoid OpenCV dependencies
        self.cv2_patcher = patch('It1_interfaces.Game.cv2')
        self.mock_cv2 = self.cv2_patcher.start()
        
        # Mock time.time for consistent timing
        self.time_patcher = patch('It1_interfaces.Game.time')
        self.mock_time = self.time_patcher.start()
        self.mock_time.time.return_value = 1000.0  # Fixed timestamp
        
        # Mock all imported component classes
        self.statistics_manager_patcher = patch('It1_interfaces.Game.StatisticsManager')
        self.mock_statistics_manager_class = self.statistics_manager_patcher.start()
        
        self.input_manager_patcher = patch('It1_interfaces.Game.ThreadedInputManager')
        self.mock_input_manager_class = self.input_manager_patcher.start()
        
        self.game_ui_patcher = patch('It1_interfaces.Game.GameUI')
        self.mock_game_ui_class = self.game_ui_patcher.start()
        
        # Set up mock instances
        self.mock_statistics_manager = Mock()
        self.mock_statistics_manager_class.return_value = self.mock_statistics_manager
        
        self.mock_input_manager = Mock()
        self.mock_input_manager_class.return_value = self.mock_input_manager
        
        self.mock_game_ui = Mock()
        self.mock_game_ui_class.return_value = self.mock_game_ui
        
        # Mock pygame components
        self.mock_pygame.init.return_value = None
        self.mock_pygame.display.set_mode.return_value = Mock()
        self.mock_pygame.time.Clock.return_value = Mock()
        self.mock_pygame.font.Font.return_value = Mock()
        self.mock_pygame.font.init.return_value = None
        
        # Mock cv2 components
        self.mock_cv2.COLOR_BGRA2RGB = 0
        self.mock_cv2.COLOR_BGR2RGB = 1
        self.mock_cv2.cvtColor.return_value = Mock()
        
        # Create mock pieces and board for Game constructor
        self.mock_pieces_list, self.mock_pieces_dict = self._create_mock_pieces()
        self.mock_board = self._create_mock_board()

    def tearDown(self):
        """Clean up after each test method."""
        self.pygame_patcher.stop()
        self.cv2_patcher.stop()
        self.time_patcher.stop()
        self.statistics_manager_patcher.stop()
        self.input_manager_patcher.stop()
        self.game_ui_patcher.stop()

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

    def test_game_initialization(self):
        """Test Game class initialization with proper setup."""
        # Create game instance
        game = Game(self.mock_pieces_list, self.mock_board)
        
        # Verify component initialization
        self.mock_statistics_manager_class.assert_called_once()
        self.mock_input_manager_class.assert_called_once()
        
        # Verify game attributes
        self.assertIsNotNone(game.board)
        self.assertIsNotNone(game.pieces)
        self.assertIsInstance(game.user_input_queue, queue.Queue)
        self.assertEqual(game.start_time, 1000.0)
        self.assertFalse(game._should_quit)
        self.assertEqual(len(game.pieces), 3)  # 3 mock pieces

    def test_game_initialization_with_event_bus(self):
        """Test Game initialization with event bus."""
        mock_event_bus = Mock()
        
        game = Game(self.mock_pieces_list, self.mock_board, event_bus=mock_event_bus)
        
        self.assertEqual(game.event_bus, mock_event_bus)

    def test_game_initialization_with_managers(self):
        """Test Game initialization with custom managers."""
        mock_score_manager = Mock()
        mock_move_logger = Mock()
        
        game = Game(self.mock_pieces_list, self.mock_board, 
                   score_manager=mock_score_manager, move_logger=mock_move_logger)
        
        self.assertEqual(game.score_manager, mock_score_manager)
        self.assertEqual(game.move_logger, mock_move_logger)

    def test_game_time_ms(self):
        """Test game time calculation in milliseconds."""
        game = Game(self.mock_pieces_list, self.mock_board)
        
        # Mock different current time - reset the time mock after game creation
        with patch('It1_interfaces.Game.time.time', return_value=1005.5):
            result = game.game_time_ms()
        
        # Should return (1005.5 - 1000.0) * 1000 = 5500ms
        self.assertEqual(result, 5500)

    def test_clone_board(self):
        """Test board cloning functionality."""
        game = Game(self.mock_pieces_list, self.mock_board)
        
        result = game.clone_board()
        
        self.mock_board.clone.assert_called_once()
        self.assertEqual(result, self.mock_board)

    def test_process_input_valid_piece(self):
        """Test processing input for valid piece."""
        game = Game(self.mock_pieces_list, self.mock_board)
        
        # Create test command
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
        game = Game(self.mock_pieces_list, self.mock_board)
        
        # Create command for non-existent piece
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
        game = Game(self.mock_pieces_list, self.mock_board)
        
        # Remove black king
        del game.pieces["KB1"]
        
        result = game._is_win()
        
        self.assertTrue(result)

    def test_win_condition_both_kings_present(self):
        """Test no win when both kings are present."""
        game = Game(self.mock_pieces_list, self.mock_board)
        
        result = game._is_win()
        
        self.assertFalse(result)

    def test_win_condition_no_kings(self):
        """Test win detection when no kings remain."""
        game = Game(self.mock_pieces_list, self.mock_board)
        
        # Remove both kings
        del game.pieces["KB1"]
        del game.pieces["KW1"]
        
        result = game._is_win()
        
        self.assertTrue(result)

    def test_announce_win_white_wins(self):
        """Test win announcement when white wins."""
        game = Game(self.mock_pieces_list, self.mock_board)
        
        # Remove black king (white wins)
        del game.pieces["KB1"]
        
        # Mock the wait for key press part
        mock_events = [Mock()]
        mock_events[0].type = self.mock_pygame.KEYDOWN
        
        with patch('builtins.print') as mock_print:
            with patch('It1_interfaces.Game.pygame.event.get', return_value=mock_events):
                game._announce_win()
                
                # Verify win message for white
                mock_print.assert_any_call("🎉 Game Over! White wins! 🎉")

    def test_announce_win_draw(self):
        """Test win announcement for draw condition."""
        game = Game(self.mock_pieces_list, self.mock_board)
        
        # Remove both kings (draw)
        del game.pieces["KB1"]
        del game.pieces["KW1"]
        
        # Mock the wait for key press part
        mock_events = [Mock()]
        mock_events[0].type = self.mock_pygame.KEYDOWN
        
        with patch('builtins.print') as mock_print:
            with patch('It1_interfaces.Game.pygame.event.get', return_value=mock_events):
                game._announce_win()
                
                # Verify draw message
                mock_print.assert_any_call("💀 Game Over! Both kings have fallen - It's a draw! 💀")

    def test_resolve_collisions_no_collision(self):
        """Test collision resolution when pieces are separate."""
        game = Game(self.mock_pieces_list, self.mock_board)
        
        # Set pieces at different positions
        game.pieces["KW1"].current_state.physics.get_pos.return_value = (7, 4)
        game.pieces["KB1"].current_state.physics.get_pos.return_value = (0, 4)
        game.pieces["PW1"].current_state.physics.get_pos.return_value = (6, 0)
        
        initial_piece_count = len(game.pieces)
        
        game._resolve_collisions()
        
        # No pieces should be removed
        self.assertEqual(len(game.pieces), initial_piece_count)

    def test_resolve_collisions_enemy_capture(self):
        """Test collision resolution with enemy capture."""
        game = Game(self.mock_pieces_list, self.mock_board)
        
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

    def test_resolve_collisions_friendly_collision(self):
        """Test collision resolution between same-color pieces."""
        game = Game(self.mock_pieces_list, self.mock_board)
        
        # Add another white piece
        white_pawn2 = Mock()
        white_pawn2.piece_id = "PW2"
        white_pawn2.piece_type = "P"
        white_pawn2.color = "White"
        white_pawn2.current_state.physics.current_cell = (5, 5)
        white_pawn2.current_state.physics.is_moving = True
        white_pawn2.current_state.state = "move"
        game.pieces["PW2"] = white_pawn2
        
        # Set both white pieces at same position
        collision_pos = (5, 5)
        game.pieces["PW1"].current_state.physics.get_pos.return_value = collision_pos
        white_pawn2.current_state.physics.get_pos.return_value = collision_pos
        
        # Set PW1 as stationary, PW2 as moving
        game.pieces["PW1"].current_state.physics.is_moving = False
        game.pieces["PW1"].current_state.state = "idle"
        
        # Set other pieces away
        game.pieces["KW1"].current_state.physics.get_pos.return_value = (7, 4)
        game.pieces["KB1"].current_state.physics.get_pos.return_value = (0, 4)
        
        game._resolve_collisions()
        
        # Both pieces should remain, moving piece should be blocked
        self.assertIn("PW1", game.pieces)
        self.assertIn("PW2", game.pieces)

    def test_handle_friendly_collision(self):
        """Test handling of friendly collision."""
        game = Game(self.mock_pieces_list, self.mock_board)
        
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

    def test_block_piece_movement(self):
        """Test blocking a piece's movement."""
        game = Game(self.mock_pieces_list, self.mock_board)
        
        piece = Mock()
        piece.piece_id = "test_piece"
        piece.current_state.physics.current_cell = (3, 3)
        
        game._block_piece_movement(piece)
        
        # Verify piece physics are reset
        self.assertEqual(piece.current_state.physics.target_cell, (3, 3))
        self.assertFalse(piece.current_state.physics.is_moving)
        piece.on_command.assert_called_once()

    def test_handle_enemy_collision(self):
        """Test handling of enemy collision."""
        game = Game(self.mock_pieces_list, self.mock_board)
        
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

    @patch('It1_interfaces.Game.pygame.event.get')
    def test_run_game_loop_quit_event(self, mock_get_events):
        """Test game loop with quit event."""
        game = Game(self.mock_pieces_list, self.mock_board)
        
        # Mock pygame QUIT event
        quit_event = Mock()
        quit_event.type = self.mock_pygame.QUIT
        mock_get_events.return_value = [quit_event]
        
        # Mock input manager method properly
        with patch.object(game.input_manager, 'get_all_selections') as mock_selections:
            mock_selections.return_value = {
                'A': {'pos': (0, 0), 'color': (255, 0, 0), 'selected': None},
                'B': {'pos': (0, 0), 'color': (0, 0, 255), 'selected': None}
            }
            
            with patch.object(game, '_is_win', return_value=True):
                with patch.object(game, '_announce_win'):
                    game.run()
        
        # Verify quit flag was set
        self.assertTrue(game._should_quit)

    def test_run_game_with_event_bus(self):
        """Test game run with event bus integration."""
        mock_event_bus = Mock()
        game = Game(self.mock_pieces_list, self.mock_board, event_bus=mock_event_bus)
        
        with patch.object(game, '_is_win', return_value=True):
            with patch.object(game, '_announce_win'):
                with patch('It1_interfaces.Game.pygame.event.get', return_value=[]):
                    game.run()
        
        # Verify event bus calls - the time value will be calculated during game run
        calls = mock_event_bus.publish.call_args_list
        
        # Check that GAME_STARTED was called
        game_started_called = any(call.args[0] == GAME_STARTED for call in calls)
        self.assertTrue(game_started_called, "GAME_STARTED event should be published")
        
        # Check that GAME_ENDED was called  
        game_ended_called = any(call.args[0] == GAME_ENDED for call in calls)
        self.assertTrue(game_ended_called, "GAME_ENDED event should be published")

    def test_draw_method_integration(self):
        """Test drawing method integration."""
        game = Game(self.mock_pieces_list, self.mock_board)
        
        # Mock board image with proper shape attribute
        mock_board_img = Mock()
        mock_board_img.img = Mock()
        mock_board_img.img.shape = (100, 100, 3)  # Use tuple instead of list, BGR format
        game.board.clone.return_value = mock_board_img
        
        # Mock input selections using patch
        with patch.object(game.input_manager, 'get_all_selections') as mock_selections:
            mock_selections.return_value = {
                'A': {'pos': (0, 0), 'color': (255, 0, 0), 'selected': None},
                'B': {'pos': (1, 1), 'color': (0, 0, 255), 'selected': None}
            }
            
            # Mock cv2 conversion
            mock_rgb_img = Mock()
            self.mock_cv2.cvtColor.return_value = mock_rgb_img
            
            # Mock pygame surface
            mock_surface = Mock()
            self.mock_pygame.surfarray.make_surface.return_value = mock_surface
            
            # Should not raise exception
            game._draw()
            
            # Verify cv2 color conversion was called
            self.mock_cv2.cvtColor.assert_called_once()
            
            # Verify pygame surface creation
            self.mock_pygame.surfarray.make_surface.assert_called_once()
            
            # Verify screen operations
            game.screen.fill.assert_called_once_with((0, 0, 0))
            game.screen.blit.assert_called_once()
            self.mock_pygame.display.flip.assert_called_once()


if __name__ == '__main__':
    unittest.main()
