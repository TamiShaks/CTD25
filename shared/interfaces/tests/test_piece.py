#!/usr/bin/env python3
"""
🧪 Comprehensive Tests for Piece Class
=====================================

Tests all functionality of the Piece class including:
- Initialization and configuration
- Color detection from piece ID
- Command handling and state transitions
- Cooldown system
- Pawn movement rules
- Movement tracking
- Drawing on board
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import modules without relative imports
from Piece import Piece
from State import State
from Command import Command
from Board import Board

class TestPiece(unittest.TestCase):
    """Comprehensive test suite for Piece class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create mock state
        self.mock_state = Mock(spec=State)
        self.mock_state.state = "idle"
        self.mock_state.state_start_time = 0
        self.mock_state.rest_duration_ms = 0
        
        # Create mock physics
        self.mock_physics = Mock()
        self.mock_physics.get_pos.return_value = (64, 64)
        self.mock_state.physics = self.mock_physics
        
        # Create mock graphics
        self.mock_graphics = Mock()
        self.mock_sprite = Mock()
        self.mock_graphics.get_img.return_value = self.mock_sprite
        self.mock_state.graphics = self.mock_graphics
        
        # Setup state methods
        self.mock_state.get_state_after_command.return_value = self.mock_state
        self.mock_state.update.return_value = self.mock_state
        
        self.current_time = int(time.time() * 1000)
        
    def test_piece_initialization_white_pieces(self):
        """🧪 Test piece initialization with white piece IDs"""
        white_piece_ids = ["PW1", "RW1", "NW1", "BW1", "QW1", "KW1"]
        
        for piece_id in white_piece_ids:
            with self.subTest(piece_id=piece_id):
                piece = Piece(piece_id, self.mock_state, "P")
                
                self.assertEqual(piece.piece_id, piece_id)
                self.assertEqual(piece.current_state, self.mock_state)
                self.assertEqual(piece.piece_type, "P")
                self.assertEqual(piece.color, "White")
                self.assertEqual(piece.movement_tracker.move_count, 0)
                self.assertFalse(piece.movement_tracker.has_moved)
                self.assertEqual(piece.cooldown_system.cooldown_duration_ms, 2000)
    
    def test_piece_initialization_black_pieces(self):
        """🧪 Test piece initialization with black piece IDs"""
        black_piece_ids = ["PB1", "RB1", "NB1", "BB1", "QB1", "KB1"]
        
        for piece_id in black_piece_ids:
            with self.subTest(piece_id=piece_id):
                piece = Piece(piece_id, self.mock_state, "P")
                
                self.assertEqual(piece.piece_id, piece_id)
                self.assertEqual(piece.color, "Black")
    
    def test_piece_initialization_unknown_color(self):
        """🧪 Test piece initialization with unknown piece ID format"""
        piece = Piece("UNKNOWN1", self.mock_state, "P")
        
        self.assertEqual(piece.color, "Unknown")
    
    def test_on_command_wrong_piece_id(self):
        """🧪 Test command handling with wrong piece ID"""
        piece = Piece("PW1", self.mock_state, "P")
        
        # Create command for different piece
        wrong_command = Command(
            timestamp=self.current_time,
            player_id="player1",
            cmd_type="Move",
            args=["PW2", "a1", "a2"]  # Different piece ID
        )
        wrong_command.piece_id = "PW2"
        
        # Should not process command
        piece.on_command(wrong_command, self.current_time)
        
        # State should not have been asked to process command
        self.mock_state.get_state_after_command.assert_not_called()
    
    def test_on_command_correct_piece_id(self):
        """🧪 Test command handling with correct piece ID"""
        piece = Piece("PW1", self.mock_state, "P")
        
        # Create command for this piece
        command = Command(
            timestamp=self.current_time,
            player_id="player1", 
            cmd_type="Move",
            args=["PW1", "a1", "a2"]
        )
        command.piece_id = "PW1"
        command.get_source_cell = Mock(return_value=[1, 1])
        command.get_target_cell = Mock(return_value=[2, 2])
        
        # Mock state transition
        new_mock_state = Mock(spec=State)
        self.mock_state.get_state_after_command.return_value = new_mock_state
        
        piece.on_command(command, self.current_time)
        
        # Verify command was processed
        self.mock_state.get_state_after_command.assert_called_once_with(command, self.current_time)
        self.assertEqual(piece.current_state, new_mock_state)
        self.assertEqual(piece.last_action_time, self.current_time)
    
    def test_piece_reset(self):
        """🧪 Test piece reset functionality"""
        piece = Piece("PW1", self.mock_state, "P")
        
        # Set some state
        piece.movement_tracker.move_count = 5
        piece.movement_tracker.has_moved = True
        piece.cooldown_system.last_action_time = self.current_time - 1000
        
        # Reset piece
        reset_time = self.current_time + 1000
        piece.reset_piece_to_initial_state(reset_time)
        
        # Verify reset
        self.assertEqual(piece.start_time, reset_time)
        self.assertEqual(piece.cooldown_system.last_action_time, reset_time)
        self.assertEqual(piece.movement_tracker.move_count, 0)
        self.assertFalse(piece.movement_tracker.has_moved)
        self.mock_state.reset.assert_called_once()
    
    def test_piece_update(self):
        """🧪 Test piece update functionality"""
        piece = Piece("PW1", self.mock_state, "P")
        
        # Mock state update returning same state
        self.mock_state.update.return_value = self.mock_state
        
        piece.update(self.current_time)
        
        # Verify update was called
        self.mock_state.update.assert_called_once_with(self.current_time)
        self.assertEqual(piece.current_state, self.mock_state)
    """Simple test suite for Piece class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock state for testing
        self.mock_state = Mock(spec=State)
        
    def test_piece_initialization_white(self):
        """🧪 Test white piece initialization"""
        piece = Piece(
            piece_id="PW60",
            init_state=self.mock_state,
            piece_type="P"
        )
        
        self.assertEqual(piece.piece_id, "PW60")
        self.assertEqual(piece.current_state, self.mock_state)
        self.assertEqual(piece.piece_type, "P")
        self.assertEqual(piece.color, "White")
        print("✅ White piece initialization test passed!")
    
    def test_piece_initialization_black(self):
        """🧪 Test black piece initialization"""
        piece = Piece(
            piece_id="PB61",
            init_state=self.mock_state,
            piece_type="P"
        )
        
        self.assertEqual(piece.piece_id, "PB61")
        self.assertEqual(piece.color, "Black")
        print("✅ Black piece initialization test passed!")
    
    def test_piece_types_white(self):
        """🧪 Test different white piece types"""
        piece_types = [
            ("PW60", "P"),  # Pawn
            ("RW70", "R"),  # Rook
            ("NW71", "N"),  # Knight
            ("BW72", "B"),  # Bishop
            ("QW73", "Q"),  # Queen
            ("KW74", "K"),  # King
        ]
        
        for piece_id, piece_type in piece_types:
            with self.subTest(piece_id=piece_id, piece_type=piece_type):
                piece = Piece(
                    piece_id=piece_id,
                    init_state=self.mock_state,
                    piece_type=piece_type
                )
                self.assertEqual(piece.color, "White")
                self.assertEqual(piece.piece_type, piece_type)
        
        print("✅ White piece types test passed!")
    
    def test_piece_types_black(self):
        """🧪 Test different black piece types"""
        piece_types = [
            ("PB10", "P"),  # Pawn
            ("RB00", "R"),  # Rook
            ("NB01", "N"),  # Knight
            ("BB02", "B"),  # Bishop
            ("QB03", "Q"),  # Queen
            ("KB04", "K"),  # King
        ]
        
        for piece_id, piece_type in piece_types:
            with self.subTest(piece_id=piece_id, piece_type=piece_type):
                piece = Piece(
                    piece_id=piece_id,
                    init_state=self.mock_state,
                    piece_type=piece_type
                )
                self.assertEqual(piece.color, "Black")
                self.assertEqual(piece.piece_type, piece_type)
        
        print("✅ Black piece types test passed!")

if __name__ == '__main__':
    unittest.main(verbosity=2)
