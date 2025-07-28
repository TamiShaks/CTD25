"""
Comprehensive test suite for InputManager class.

Tests the input management system including:
- Input manager initialization and setup
- Player selection cursor movement
- Piece selection and deselection
- Move validation and command creation
- Chess rules integration
- Multi-player input handling
- Edge cases and error handling
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os
import queue

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Add main project directory for imports
main_dir = os.path.dirname(parent_dir)
sys.path.insert(0, main_dir)

from It1_interfaces.InputManager import InputManager
from It1_interfaces.Command import Command
from It1_interfaces.ChessRulesValidator import ChessRulesValidator


class TestInputManager(unittest.TestCase):
    """Test suite for InputManager class covering all input functionality."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock board
        self.mock_board = Mock()
        self.mock_board.H_cells = 8
        self.mock_board.W_cells = 8
        
        # Create input queue
        self.input_queue = queue.Queue()
        
        # Mock chess validator BEFORE creating InputManager
        self.chess_validator_patcher = patch('It1_interfaces.InputManager.ChessRulesValidator')
        self.mock_chess_validator_class = self.chess_validator_patcher.start()
        self.mock_chess_validator = Mock()
        self.mock_chess_validator_class.return_value = self.mock_chess_validator
        
        # Create InputManager instance (after mocking ChessRulesValidator)
        self.input_manager = InputManager(self.mock_board, self.input_queue)
        
        # Create test pieces
        self.white_king = self._create_mock_piece("KW1", "K", "White", (7, 4))
        self.white_pawn = self._create_mock_piece("PW1", "P", "White", (6, 0))
        self.black_king = self._create_mock_piece("KB1", "K", "Black", (0, 4))
        self.black_queen = self._create_mock_piece("QB1", "Q", "Black", (0, 3))
        
        # Test pieces dictionary
        self.test_pieces = {
            "KW1": self.white_king,
            "PW1": self.white_pawn,
            "KB1": self.black_king,
            "QB1": self.black_queen
        }
        
        # Mock game time function
        self.mock_game_time_func = Mock(return_value=1000)

    def tearDown(self):
        """Clean up after each test method."""
        self.chess_validator_patcher.stop()

    def _create_mock_piece(self, piece_id, piece_type, color, position):
        """Create a mock piece with required attributes."""
        piece = Mock()
        piece.piece_id = piece_id
        piece.piece_type = piece_type
        piece.color = color
        piece.current_state.physics.current_cell = position
        
        # Mock moves
        piece.current_state.moves = Mock()
        valid_moves = self._get_valid_moves_for_piece(piece_type, position)
        piece.current_state.moves.get_moves.return_value = valid_moves
        
        return piece

    def _get_valid_moves_for_piece(self, piece_type, position):
        """Get sample valid moves for a piece type."""
        row, col = position
        if piece_type == "K":  # King
            return [(row-1, col), (row+1, col), (row, col-1), (row, col+1),
                   (row-1, col-1), (row-1, col+1), (row+1, col-1), (row+1, col+1)]
        elif piece_type == "P":  # Pawn
            if row == 6:  # White pawn starting position
                return [(row-1, col), (row-2, col)]
            else:
                return [(row-1, col)]
        elif piece_type == "Q":  # Queen
            return [(i, col) for i in range(8)] + [(row, i) for i in range(8)]
        return []

    def test_input_manager_initialization(self):
        """Test InputManager initialization."""
        manager = InputManager(self.mock_board, self.input_queue)
        
        self.assertIsInstance(manager, InputManager)
        self.assertEqual(manager.board, self.mock_board)
        self.assertEqual(manager.user_input_queue, self.input_queue)
        self.assertIsNotNone(manager.chess_validator)
        
        # Check initial selection state
        self.assertIn('A', manager.selection)
        self.assertIn('B', manager.selection)
        
        # Check player A initial state
        self.assertEqual(manager.selection['A']['pos'], [0, 0])
        self.assertIsNone(manager.selection['A']['selected'])
        self.assertEqual(manager.selection['A']['color'], (255, 0, 0))
        
        # Check player B initial state
        self.assertEqual(manager.selection['B']['pos'], [7, 7])
        self.assertIsNone(manager.selection['B']['selected'])
        self.assertEqual(manager.selection['B']['color'], (0, 0, 255))

    def test_move_selection_up(self):
        """Test moving selection cursor up."""
        # Start at position [2, 2]
        self.input_manager.selection['A']['pos'] = [2, 2]
        
        self.input_manager.move_selection('A', 'up')
        
        self.assertEqual(self.input_manager.selection['A']['pos'], [1, 2])

    def test_move_selection_down(self):
        """Test moving selection cursor down."""
        # Start at position [2, 2]
        self.input_manager.selection['A']['pos'] = [2, 2]
        
        self.input_manager.move_selection('A', 'down')
        
        self.assertEqual(self.input_manager.selection['A']['pos'], [3, 2])

    def test_move_selection_left(self):
        """Test moving selection cursor left."""
        # Start at position [2, 2]
        self.input_manager.selection['A']['pos'] = [2, 2]
        
        self.input_manager.move_selection('A', 'left')
        
        self.assertEqual(self.input_manager.selection['A']['pos'], [2, 1])

    def test_move_selection_right(self):
        """Test moving selection cursor right."""
        # Start at position [2, 2]
        self.input_manager.selection['A']['pos'] = [2, 2]
        
        self.input_manager.move_selection('A', 'right')
        
        self.assertEqual(self.input_manager.selection['A']['pos'], [2, 3])

    def test_move_selection_up_boundary(self):
        """Test moving selection up at top boundary."""
        # Start at top row
        self.input_manager.selection['A']['pos'] = [0, 2]
        
        self.input_manager.move_selection('A', 'up')
        
        # Should stay at top row
        self.assertEqual(self.input_manager.selection['A']['pos'], [0, 2])

    def test_move_selection_down_boundary(self):
        """Test moving selection down at bottom boundary."""
        # Start at bottom row
        self.input_manager.selection['A']['pos'] = [7, 2]
        
        self.input_manager.move_selection('A', 'down')
        
        # Should stay at bottom row
        self.assertEqual(self.input_manager.selection['A']['pos'], [7, 2])

    def test_move_selection_left_boundary(self):
        """Test moving selection left at left boundary."""
        # Start at leftmost column
        self.input_manager.selection['A']['pos'] = [2, 0]
        
        self.input_manager.move_selection('A', 'left')
        
        # Should stay at leftmost column
        self.assertEqual(self.input_manager.selection['A']['pos'], [2, 0])

    def test_move_selection_right_boundary(self):
        """Test moving selection right at right boundary."""
        # Start at rightmost column
        self.input_manager.selection['A']['pos'] = [2, 7]
        
        self.input_manager.move_selection('A', 'right')
        
        # Should stay at rightmost column
        self.assertEqual(self.input_manager.selection['A']['pos'], [2, 7])

    def test_move_selection_invalid_direction(self):
        """Test moving selection with invalid direction."""
        initial_pos = [2, 2]
        self.input_manager.selection['A']['pos'] = initial_pos.copy()
        
        self.input_manager.move_selection('A', 'invalid')
        
        # Position should remain unchanged
        self.assertEqual(self.input_manager.selection['A']['pos'], initial_pos)

    def test_move_selection_both_players(self):
        """Test moving selection for both players independently."""
        # Set initial positions
        self.input_manager.selection['A']['pos'] = [3, 3]
        self.input_manager.selection['B']['pos'] = [4, 4]
        
        # Move player A
        self.input_manager.move_selection('A', 'up')
        # Move player B
        self.input_manager.move_selection('B', 'down')
        
        # Check both moved independently
        self.assertEqual(self.input_manager.selection['A']['pos'], [2, 3])
        self.assertEqual(self.input_manager.selection['B']['pos'], [5, 4])

    def test_select_piece_first_selection_valid_piece(self):
        """Test selecting a piece that belongs to the player."""
        # Position cursor on white king
        self.input_manager.selection['A']['pos'] = [7, 4]
        
        self.input_manager.select_piece('A', self.test_pieces, self.mock_game_time_func)
        
        # Should select the white king
        self.assertEqual(self.input_manager.selection['A']['selected'], self.white_king)

    def test_select_piece_first_selection_wrong_color(self):
        """Test selecting a piece that doesn't belong to the player."""
        # Position player A cursor on black king
        self.input_manager.selection['A']['pos'] = [0, 4]
        
        self.input_manager.select_piece('A', self.test_pieces, self.mock_game_time_func)
        
        # Should not select the black king
        self.assertIsNone(self.input_manager.selection['A']['selected'])

    def test_select_piece_first_selection_empty_square(self):
        """Test selecting an empty square."""
        # Position cursor on empty square
        self.input_manager.selection['A']['pos'] = [3, 3]
        
        self.input_manager.select_piece('A', self.test_pieces, self.mock_game_time_func)
        
        # Should not select anything
        self.assertIsNone(self.input_manager.selection['A']['selected'])

    def test_select_piece_player_b_selects_black_piece(self):
        """Test player B selecting a black piece."""
        # Position player B cursor on black queen
        self.input_manager.selection['B']['pos'] = [0, 3]
        
        self.input_manager.select_piece('B', self.test_pieces, self.mock_game_time_func)
        
        # Should select the black queen
        self.assertEqual(self.input_manager.selection['B']['selected'], self.black_queen)

    def test_select_piece_second_selection_valid_move(self):
        """Test making a valid move after selecting a piece."""
        # First select white pawn
        self.input_manager.selection['A']['pos'] = [6, 0]
        self.input_manager.select_piece('A', self.test_pieces, self.mock_game_time_func)
        self.assertEqual(self.input_manager.selection['A']['selected'], self.white_pawn)
        
        # Mock chess validator to allow the move
        self.input_manager.chess_validator.is_valid_move.return_value = True
        
        # Move cursor to valid move position
        self.input_manager.selection['A']['pos'] = [5, 0]
        
        # Mock Command.create_move_command
        with patch('It1_interfaces.InputManager.Command') as mock_command_class:
            mock_command = Mock()
            mock_command_class.create_move_command.return_value = mock_command
            
            self.input_manager.select_piece('A', self.test_pieces, self.mock_game_time_func)
            
            # Should create and queue command
            mock_command_class.create_move_command.assert_called_once_with(
                1000, "PW1", (6, 0), (5, 0)
            )
            
            # Should have queued the command
            self.assertFalse(self.input_queue.empty())
            queued_command = self.input_queue.get()
            self.assertEqual(queued_command, mock_command)
        
        # Should deselect piece after move
        self.assertIsNone(self.input_manager.selection['A']['selected'])

    def test_select_piece_second_selection_invalid_move_not_in_valid_moves(self):
        """Test making an invalid move (not in piece's valid moves)."""
        # First select white king
        self.input_manager.selection['A']['pos'] = [7, 4]
        self.input_manager.select_piece('A', self.test_pieces, self.mock_game_time_func)
        
        # Move cursor to invalid position (too far)
        self.input_manager.selection['A']['pos'] = [5, 4]
        
        # Try to make invalid move
        self.input_manager.select_piece('A', self.test_pieces, self.mock_game_time_func)
        
        # Should not queue any command
        self.assertTrue(self.input_queue.empty())
        
        # Should deselect piece
        self.assertIsNone(self.input_manager.selection['A']['selected'])

    def test_select_piece_second_selection_invalid_chess_rules(self):
        """Test making a move that violates chess rules."""
        # First select white pawn
        self.input_manager.selection['A']['pos'] = [6, 0]
        self.input_manager.select_piece('A', self.test_pieces, self.mock_game_time_func)
        
        # Mock chess validator to reject the move
        self.input_manager.chess_validator.is_valid_move.return_value = False
        
        # Move cursor to position that would be valid by piece movement but invalid by chess rules
        self.input_manager.selection['A']['pos'] = [5, 0]
        
        self.input_manager.select_piece('A', self.test_pieces, self.mock_game_time_func)
        
        # Should not queue any command
        self.assertTrue(self.input_queue.empty())
        
        # Should deselect piece
        self.assertIsNone(self.input_manager.selection['A']['selected'])

    def test_select_piece_with_target_piece(self):
        """Test making a move that captures an enemy piece."""
        # First select white king
        self.input_manager.selection['A']['pos'] = [7, 4]
        self.input_manager.select_piece('A', self.test_pieces, self.mock_game_time_func)
        
        # Position black king adjacent to white king for testing
        self.black_king.current_state.physics.current_cell = (6, 4)
        
        # Mock chess validator to allow the capture
        self.input_manager.chess_validator.is_valid_move.return_value = True
        
        # Move cursor to black king position
        self.input_manager.selection['A']['pos'] = [6, 4]
        
        with patch('It1_interfaces.InputManager.Command') as mock_command_class:
            mock_command = Mock()
            mock_command_class.create_move_command.return_value = mock_command
            
            self.input_manager.select_piece('A', self.test_pieces, self.mock_game_time_func)
            
            # Should call chess validator with target piece
            self.input_manager.chess_validator.is_valid_move.assert_called_once_with(
                self.white_king, (7, 4), (6, 4), self.black_king, self.test_pieces
            )

    def test_get_selection_player_a(self):
        """Test getting selection for player A."""
        result = self.input_manager.get_selection('A')
        
        expected = {
            'pos': [0, 0],
            'selected': None,
            'color': (255, 0, 0)
        }
        self.assertEqual(result, expected)

    def test_get_selection_player_b(self):
        """Test getting selection for player B."""
        result = self.input_manager.get_selection('B')
        
        expected = {
            'pos': [7, 7],
            'selected': None,
            'color': (0, 0, 255)
        }
        self.assertEqual(result, expected)

    def test_get_selection_after_modifications(self):
        """Test getting selection after making modifications."""
        # Modify player A selection
        self.input_manager.selection['A']['pos'] = [3, 5]
        self.input_manager.selection['A']['selected'] = self.white_king
        
        result = self.input_manager.get_selection('A')
        
        expected = {
            'pos': [3, 5],
            'selected': self.white_king,
            'color': (255, 0, 0)
        }
        self.assertEqual(result, expected)

    def test_get_all_selections(self):
        """Test getting all player selections."""
        result = self.input_manager.get_all_selections()
        
        self.assertIn('A', result)
        self.assertIn('B', result)
        self.assertEqual(result['A']['pos'], [0, 0])
        self.assertEqual(result['B']['pos'], [7, 7])
        self.assertEqual(result['A']['color'], (255, 0, 0))
        self.assertEqual(result['B']['color'], (0, 0, 255))

    def test_get_all_selections_after_changes(self):
        """Test getting all selections after making changes."""
        # Make changes to both players
        self.input_manager.selection['A']['pos'] = [2, 3]
        self.input_manager.selection['A']['selected'] = self.white_pawn
        self.input_manager.selection['B']['pos'] = [5, 1]
        self.input_manager.selection['B']['selected'] = self.black_queen
        
        result = self.input_manager.get_all_selections()
        
        self.assertEqual(result['A']['pos'], [2, 3])
        self.assertEqual(result['A']['selected'], self.white_pawn)
        self.assertEqual(result['B']['pos'], [5, 1])
        self.assertEqual(result['B']['selected'], self.black_queen)

    def test_multiple_move_sequence(self):
        """Test a complete sequence of moves."""
        # Player A selects and moves white pawn
        self.input_manager.selection['A']['pos'] = [6, 0]
        self.input_manager.select_piece('A', self.test_pieces, self.mock_game_time_func)
        
        self.input_manager.chess_validator.is_valid_move.return_value = True
        
        with patch('It1_interfaces.InputManager.Command') as mock_command_class:
            mock_command_class.create_move_command.return_value = Mock()
            
            self.input_manager.selection['A']['pos'] = [5, 0]
            self.input_manager.select_piece('A', self.test_pieces, self.mock_game_time_func)
            
            # Player B selects and moves black queen
            self.input_manager.selection['B']['pos'] = [0, 3]
            self.input_manager.select_piece('B', self.test_pieces, self.mock_game_time_func)
            
            self.input_manager.selection['B']['pos'] = [1, 3]
            self.input_manager.select_piece('B', self.test_pieces, self.mock_game_time_func)
            
            # Should have created two commands
            self.assertEqual(mock_command_class.create_move_command.call_count, 2)

    def test_board_size_variations(self):
        """Test input manager with different board sizes."""
        # Test with smaller board
        small_board = Mock()
        small_board.H_cells = 6
        small_board.W_cells = 6
        
        small_input_manager = InputManager(small_board, queue.Queue())
        
        # Test boundary movement on smaller board
        small_input_manager.selection['A']['pos'] = [5, 5]  # Bottom-right corner
        small_input_manager.move_selection('A', 'down')
        small_input_manager.move_selection('A', 'right')
        
        # Should stay at boundary
        self.assertEqual(small_input_manager.selection['A']['pos'], [5, 5])

    def test_piece_without_color_attribute(self):
        """Test handling piece without color attribute."""
        # Create piece without color attribute
        broken_piece = Mock()
        broken_piece.piece_id = "BROKEN1"
        broken_piece.current_state.physics.current_cell = (3, 3)
        del broken_piece.color  # Remove color attribute
        
        pieces_with_broken = self.test_pieces.copy()
        pieces_with_broken["BROKEN1"] = broken_piece
        
        # Position cursor on broken piece
        self.input_manager.selection['A']['pos'] = [3, 3]
        
        # Should not select piece without color
        self.input_manager.select_piece('A', pieces_with_broken, self.mock_game_time_func)
        
        self.assertIsNone(self.input_manager.selection['A']['selected'])

    def test_chess_validator_integration(self):
        """Test integration with chess validator."""
        # Select white pawn
        self.input_manager.selection['A']['pos'] = [6, 0]
        self.input_manager.select_piece('A', self.test_pieces, self.mock_game_time_func)
        
        # Mock chess validator call
        self.input_manager.chess_validator.is_valid_move.return_value = True
        
        # Attempt move
        self.input_manager.selection['A']['pos'] = [5, 0]
        
        with patch('It1_interfaces.InputManager.Command') as mock_command_class:
            mock_command_class.create_move_command.return_value = Mock()
            
            self.input_manager.select_piece('A', self.test_pieces, self.mock_game_time_func)
            
            # Verify chess validator was called with correct parameters
            self.input_manager.chess_validator.is_valid_move.assert_called_once()
            call_args = self.input_manager.chess_validator.is_valid_move.call_args[0]
            
            self.assertEqual(call_args[0], self.white_pawn)  # selected piece
            self.assertEqual(call_args[1], (6, 0))          # start position
            self.assertEqual(call_args[2], (5, 0))          # target position
            self.assertIsNone(call_args[3])                 # target piece (empty square)
            self.assertEqual(call_args[4], self.test_pieces) # all pieces

    def test_command_creation_parameters(self):
        """Test that commands are created with correct parameters."""
        # Select piece and make move
        self.input_manager.selection['A']['pos'] = [7, 4]
        self.input_manager.select_piece('A', self.test_pieces, self.mock_game_time_func)
        
        self.input_manager.chess_validator.is_valid_move.return_value = True
        self.input_manager.selection['A']['pos'] = [6, 4]
        
        with patch('It1_interfaces.InputManager.Command') as mock_command_class:
            mock_command = Mock()
            mock_command_class.create_move_command.return_value = mock_command
            
            self.input_manager.select_piece('A', self.test_pieces, self.mock_game_time_func)
            
            # Verify command creation parameters
            mock_command_class.create_move_command.assert_called_once_with(
                1000,           # timestamp
                "KW1",          # piece_id
                (7, 4),         # start_pos
                (6, 4)          # target_pos
            )

    def test_integration_realistic_game_flow(self):
        """Test realistic game flow with multiple players and moves."""
        self.input_manager.chess_validator.is_valid_move.return_value = True
        
        with patch('It1_interfaces.InputManager.Command') as mock_command_class:
            mock_command_class.create_move_command.return_value = Mock()
            
            # Player A turn: move white pawn
            self.input_manager.move_selection('A', 'down')  # Move to [1, 0]
            self.input_manager.move_selection('A', 'down')  # Move to [2, 0]
            self.input_manager.move_selection('A', 'down')  # Move to [3, 0]
            self.input_manager.move_selection('A', 'down')  # Move to [4, 0]
            self.input_manager.move_selection('A', 'down')  # Move to [5, 0]
            self.input_manager.move_selection('A', 'down')  # Move to [6, 0]
            
            # Select white pawn
            self.input_manager.select_piece('A', self.test_pieces, self.mock_game_time_func)
            self.assertEqual(self.input_manager.selection['A']['selected'], self.white_pawn)
            
            # Move pawn forward
            self.input_manager.move_selection('A', 'up')    # Move to [5, 0]
            self.input_manager.select_piece('A', self.test_pieces, self.mock_game_time_func)
            
            # Player B turn: move black queen
            self.input_manager.move_selection('B', 'up')    # Move to [6, 7]
            self.input_manager.move_selection('B', 'up')    # Move to [5, 7]
            self.input_manager.move_selection('B', 'up')    # Move to [4, 7]
            self.input_manager.move_selection('B', 'up')    # Move to [3, 7]
            self.input_manager.move_selection('B', 'up')    # Move to [2, 7]
            self.input_manager.move_selection('B', 'up')    # Move to [1, 7]
            self.input_manager.move_selection('B', 'up')    # Move to [0, 7]
            self.input_manager.move_selection('B', 'left')  # Move to [0, 6]
            self.input_manager.move_selection('B', 'left')  # Move to [0, 5]
            self.input_manager.move_selection('B', 'left')  # Move to [0, 4]
            self.input_manager.move_selection('B', 'left')  # Move to [0, 3]
            
            # Select black queen
            self.input_manager.select_piece('B', self.test_pieces, self.mock_game_time_func)
            self.assertEqual(self.input_manager.selection['B']['selected'], self.black_queen)
            
            # Move queen
            self.input_manager.move_selection('B', 'down')  # Move to [1, 3]
            self.input_manager.select_piece('B', self.test_pieces, self.mock_game_time_func)
            
            # Should have created two commands
            self.assertEqual(mock_command_class.create_move_command.call_count, 2)


if __name__ == '__main__':
    unittest.main()
