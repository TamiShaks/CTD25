"""
Comprehensive test suite for ChessRulesValidator class.

Tests chess rule validation including:
- Pawn movement rules (forward, diagonal capture, first move)
- Friendly fire prevention
- Path blocking detection  
- Color-specific movement directions
- Chess rule compliance
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from ChessRulesValidator import ChessRulesValidator


class TestChessRulesValidator(unittest.TestCase):
    """Test suite for ChessRulesValidator class covering all chess rules."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.validator = ChessRulesValidator()
        
        # Create mock pieces for testing
        self.white_pawn = self._create_mock_pawn("White", "PW1", has_moved=False)
        self.black_pawn = self._create_mock_pawn("Black", "PB1", has_moved=False)
        self.white_pawn_moved = self._create_mock_pawn("White", "PW2", has_moved=True)
        
        self.white_king = self._create_mock_piece("K", "White", "KW1")
        self.black_king = self._create_mock_piece("K", "Black", "KB1")
        
        self.white_rook = self._create_mock_piece("R", "White", "RW1")
        self.black_rook = self._create_mock_piece("R", "Black", "RB1")

    def _create_mock_pawn(self, color, piece_id, has_moved=False):
        """Create a mock pawn piece."""
        pawn = Mock()
        pawn.piece_type = "P"
        pawn.color = color
        pawn.piece_id = piece_id
        pawn.has_moved = has_moved
        
        # Mock moves object for path blocking
        pawn.current_state = Mock()
        pawn.current_state.moves = Mock()
        pawn.current_state.moves.is_path_blocked.return_value = False
        
        return pawn

    def _create_mock_piece(self, piece_type, color, piece_id):
        """Create a mock piece of any type."""
        piece = Mock()
        piece.piece_type = piece_type
        piece.color = color
        piece.piece_id = piece_id
        
        # Mock moves object for path blocking
        piece.current_state = Mock()
        piece.current_state.moves = Mock()
        piece.current_state.moves.is_path_blocked.return_value = False
        
        return piece

    def test_validator_initialization(self):
        """Test ChessRulesValidator initialization."""
        validator = ChessRulesValidator()
        self.assertIsInstance(validator, ChessRulesValidator)

    def test_friendly_fire_prevention_same_color(self):
        """Test that pieces cannot capture their own color."""
        # White pawn trying to capture white king
        result = self.validator.is_valid_move(
            piece=self.white_pawn,
            start_pos=(6, 0),
            target_pos=(5, 1),
            target_piece=self.white_king,
            all_pieces={}
        )
        
        self.assertFalse(result, "Friendly fire should be prevented")

    def test_friendly_fire_prevention_different_color(self):
        """Test that pieces can capture opposite color."""
        # White pawn trying to capture black king (diagonal)
        result = self.validator.is_valid_move(
            piece=self.white_pawn,
            start_pos=(6, 0),
            target_pos=(5, 1),
            target_piece=self.black_king,
            all_pieces={}
        )
        
        self.assertTrue(result, "Opposite color capture should be allowed")

    def test_pawn_single_step_forward_white(self):
        """Test white pawn single step forward movement."""
        result = self.validator._is_valid_pawn_move(
            pawn=self.white_pawn,
            start_pos=(6, 0),
            target_pos=(5, 0),  # One step forward (up)
            target_piece=None
        )
        
        self.assertTrue(result, "White pawn should move one step forward")

    def test_pawn_single_step_forward_black(self):
        """Test black pawn single step forward movement."""
        result = self.validator._is_valid_pawn_move(
            pawn=self.black_pawn,
            start_pos=(1, 0),
            target_pos=(2, 0),  # One step forward (down)
            target_piece=None
        )
        
        self.assertTrue(result, "Black pawn should move one step forward")

    def test_pawn_double_step_first_move_white(self):
        """Test white pawn double step on first move."""
        result = self.validator._is_valid_pawn_move(
            pawn=self.white_pawn,  # has_moved=False
            start_pos=(6, 0),
            target_pos=(4, 0),  # Two steps forward
            target_piece=None
        )
        
        self.assertTrue(result, "White pawn should move two steps on first move")

    def test_pawn_double_step_first_move_black(self):
        """Test black pawn double step on first move."""
        result = self.validator._is_valid_pawn_move(
            pawn=self.black_pawn,  # has_moved=False
            start_pos=(1, 0),
            target_pos=(3, 0),  # Two steps forward
            target_piece=None
        )
        
        self.assertTrue(result, "Black pawn should move two steps on first move")

    def test_pawn_double_step_after_moved(self):
        """Test pawn cannot double step after already moved."""
        result = self.validator._is_valid_pawn_move(
            pawn=self.white_pawn_moved,  # has_moved=True
            start_pos=(5, 0),
            target_pos=(3, 0),  # Two steps forward
            target_piece=None
        )
        
        self.assertFalse(result, "Pawn should not move two steps after first move")

    def test_pawn_diagonal_capture_white(self):
        """Test white pawn diagonal capture."""
        result = self.validator._is_valid_pawn_move(
            pawn=self.white_pawn,
            start_pos=(6, 0),
            target_pos=(5, 1),  # Diagonal up-right
            target_piece=self.black_pawn  # Enemy piece present
        )
        
        self.assertTrue(result, "White pawn should capture diagonally")

    def test_pawn_diagonal_capture_black(self):
        """Test black pawn diagonal capture."""
        result = self.validator._is_valid_pawn_move(
            pawn=self.black_pawn,
            start_pos=(1, 1),
            target_pos=(2, 0),  # Diagonal down-left
            target_piece=self.white_pawn  # Enemy piece present
        )
        
        self.assertTrue(result, "Black pawn should capture diagonally")

    def test_pawn_diagonal_move_without_capture(self):
        """Test pawn cannot move diagonally without capture."""
        result = self.validator._is_valid_pawn_move(
            pawn=self.white_pawn,
            start_pos=(6, 0),
            target_pos=(5, 1),  # Diagonal
            target_piece=None  # No piece to capture
        )
        
        self.assertFalse(result, "Pawn should not move diagonally without capture")

    def test_pawn_backward_movement(self):
        """Test pawn cannot move backward."""
        # White pawn trying to move backward (down)
        result = self.validator._is_valid_pawn_move(
            pawn=self.white_pawn,
            start_pos=(5, 0),
            target_pos=(6, 0),  # Backward for white
            target_piece=None
        )
        
        self.assertFalse(result, "Pawn should not move backward")

    def test_pawn_sideways_movement(self):
        """Test pawn cannot move sideways."""
        result = self.validator._is_valid_pawn_move(
            pawn=self.white_pawn,
            start_pos=(6, 0),
            target_pos=(6, 1),  # Sideways
            target_piece=None
        )
        
        self.assertFalse(result, "Pawn should not move sideways")

    def test_pawn_invalid_diagonal_distance(self):
        """Test pawn cannot move more than one square diagonally."""
        result = self.validator._is_valid_pawn_move(
            pawn=self.white_pawn,
            start_pos=(6, 0),
            target_pos=(4, 2),  # Two squares diagonally
            target_piece=self.black_pawn
        )
        
        self.assertFalse(result, "Pawn should not move more than one square diagonally")

    def test_non_pawn_piece_always_valid(self):
        """Test that non-pawn pieces pass pawn validation."""
        result = self.validator._is_valid_pawn_move(
            pawn=self.white_king,  # Not a pawn
            start_pos=(7, 4),
            target_pos=(6, 4),
            target_piece=None
        )
        
        self.assertTrue(result, "Non-pawn pieces should pass pawn validation")

    def test_path_blocking_prevents_movement(self):
        """Test that path blocking prevents movement."""
        # Mock path blocking
        self.white_rook.current_state.moves.is_path_blocked.return_value = True
        
        result = self.validator.is_valid_move(
            piece=self.white_rook,
            start_pos=(7, 0),
            target_pos=(7, 7),  # Horizontal move
            target_piece=None,
            all_pieces={"blocking_piece": self.white_pawn}
        )
        
        self.assertFalse(result, "Path blocking should prevent movement")

    def test_path_clear_allows_movement(self):
        """Test that clear path allows movement."""
        # Mock path clear
        self.white_rook.current_state.moves.is_path_blocked.return_value = False
        
        result = self.validator.is_valid_move(
            piece=self.white_rook,
            start_pos=(7, 0),
            target_pos=(7, 7),  # Horizontal move
            target_piece=None,
            all_pieces={}
        )
        
        self.assertTrue(result, "Clear path should allow movement")

    def test_path_blocking_called_with_correct_parameters(self):
        """Test that path blocking is called with correct parameters."""
        all_pieces = {"piece1": self.white_pawn}
        
        self.validator.is_valid_move(
            piece=self.white_rook,
            start_pos=(7, 0),
            target_pos=(7, 7),
            target_piece=None,
            all_pieces=all_pieces
        )
        
        # Verify path blocking was called with correct parameters
        self.white_rook.current_state.moves.is_path_blocked.assert_called_once_with(
            (7, 0), (7, 7), "R", all_pieces
        )

    def test_target_piece_without_color_attribute(self):
        """Test handling of target piece without color attribute."""
        target_piece_no_color = Mock()
        # Explicitly don't set color attribute
        
        result = self.validator.is_valid_move(
            piece=self.white_pawn,
            start_pos=(6, 0),
            target_pos=(5, 1),
            target_piece=target_piece_no_color,
            all_pieces={}
        )
        
        # Should not crash and should proceed to pawn validation
        self.assertTrue(result, "Should handle pieces without color attribute")

    def test_piece_without_color_attribute(self):
        """Test handling of moving piece without color attribute."""
        piece_no_color = Mock()
        piece_no_color.piece_type = "P"
        # Explicitly don't set color attribute
        
        result = self.validator.is_valid_move(
            piece=piece_no_color,
            start_pos=(6, 0),
            target_pos=(5, 0),
            target_piece=None,
            all_pieces={}
        )
        
        # Should not crash - would fail in pawn validation due to missing color
        # This tests robustness of the friendly fire check
        self.assertIsInstance(result, bool, "Should return boolean even with missing attributes")

    def test_pawn_complex_diagonal_scenarios(self):
        """Test complex pawn diagonal capture scenarios."""
        test_cases = [
            # (start_pos, target_pos, target_piece, expected, description)
            ((6, 0), (5, 1), self.black_pawn, True, "White pawn diagonal capture right"),
            ((6, 1), (5, 0), self.black_pawn, True, "White pawn diagonal capture left"),
            ((1, 0), (2, 1), self.white_pawn, True, "Black pawn diagonal capture right"),
            ((1, 1), (2, 0), self.white_pawn, True, "Black pawn diagonal capture left"),
            ((6, 0), (5, 1), None, False, "White pawn diagonal move without capture"),
            ((1, 0), (2, 1), None, False, "Black pawn diagonal move without capture"),
        ]
        
        for start_pos, target_pos, target_piece, expected, description in test_cases:
            with self.subTest(description=description):
                pawn = self.white_pawn if start_pos[0] == 6 else self.black_pawn
                result = self.validator._is_valid_pawn_move(pawn, start_pos, target_pos, target_piece)
                self.assertEqual(result, expected, f"{description} should be {expected}")

    def test_integration_pawn_moves_in_game_context(self):
        """Test pawn moves in full game context."""
        # White pawn standard move
        result = self.validator.is_valid_move(
            piece=self.white_pawn,
            start_pos=(6, 0),
            target_pos=(5, 0),
            target_piece=None,
            all_pieces={}
        )
        
        self.assertTrue(result, "Standard pawn move should be valid in game context")
        
        # White pawn capture black piece
        result = self.validator.is_valid_move(
            piece=self.white_pawn,
            start_pos=(6, 0),
            target_pos=(5, 1),
            target_piece=self.black_pawn,
            all_pieces={}
        )
        
        self.assertTrue(result, "Pawn capture should be valid in game context")
        
        # White pawn try to capture white piece (friendly fire)
        result = self.validator.is_valid_move(
            piece=self.white_pawn,
            start_pos=(6, 0),
            target_pos=(5, 1),
            target_piece=self.white_king,
            all_pieces={}
        )
        
        self.assertFalse(result, "Friendly fire should be prevented in game context")


if __name__ == '__main__':
    unittest.main()
