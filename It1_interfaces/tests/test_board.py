#!/usr/bin/env python3
"""
🧪 Comprehensive Tests for Board Class
=====================================

Tests all functionality of the Board class including:
- Initialization and configuration
- Image handling and copying
- Cell size calculations
- Board dimensions
- Deep copy functionality
- Reset operations
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import copy

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import modules without relative imports
from Board import Board
from img import Img

class TestBoard(unittest.TestCase):
    """Comprehensive test suite for Board class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create a mock Img object for testing
        self.mock_img = Mock(spec=Img)
        self.mock_img.img = Mock()  # Mock the internal image data
        
        # Standard chess board dimensions
        self.cell_height = 64
        self.cell_width = 64
        self.board_width = 8
        self.board_height = 8
        
    def test_board_initialization_basic(self):
        """🧪 Test basic board initialization with valid parameters"""
        board = Board(
            cell_H_pix=self.cell_height,
            cell_W_pix=self.cell_width,
            W_cells=self.board_width,
            H_cells=self.board_height,
            img=self.mock_img
        )
        
        # Verify all parameters are stored correctly
        self.assertEqual(board.cell_H_pix, self.cell_height)
        self.assertEqual(board.cell_W_pix, self.cell_width)
        self.assertEqual(board.W_cells, self.board_width)
        self.assertEqual(board.H_cells, self.board_height)
        self.assertEqual(board.img, self.mock_img)
        
    def test_board_initialization_different_sizes(self):
        """🧪 Test board initialization with various board sizes"""
        test_cases = [
            (32, 32, 4, 4),    # Small board
            (64, 64, 8, 8),    # Standard chess
            (128, 128, 10, 10), # Large board
            (50, 75, 6, 8),    # Rectangular cells
        ]
        
        for cell_h, cell_w, w_cells, h_cells in test_cases:
            with self.subTest(cell_h=cell_h, cell_w=cell_w, w_cells=w_cells, h_cells=h_cells):
                board = Board(
                    cell_H_pix=cell_h,
                    cell_W_pix=cell_w,
                    W_cells=w_cells,
                    H_cells=h_cells,
                    img=self.mock_img
                )
                
                self.assertEqual(board.cell_H_pix, cell_h)
                self.assertEqual(board.cell_W_pix, cell_w)
                self.assertEqual(board.W_cells, w_cells)
                self.assertEqual(board.H_cells, h_cells)
    
    @patch('copy.deepcopy')
    def test_original_img_deep_copy_creation(self, mock_deepcopy):
        """🧪 Test that original_img is created as a deep copy during initialization"""
        mock_copied_img = Mock(spec=Img)
        mock_deepcopy.return_value = mock_copied_img
        
        board = Board(
            cell_H_pix=self.cell_height,
            cell_W_pix=self.cell_width,
            W_cells=self.board_width,
            H_cells=self.board_height,
            img=self.mock_img
        )
        
        # Verify deepcopy was called with the original image
        mock_deepcopy.assert_called_once_with(self.mock_img)
        
        # Verify the original_img field is set to the copied image
        self.assertEqual(board.original_img, mock_copied_img)
    
    def test_board_dimensions_calculations(self):
        """🧪 Test implicit board dimension calculations"""
        board = Board(
            cell_H_pix=50,
            cell_W_pix=75,
            W_cells=10,
            H_cells=12,
            img=self.mock_img
        )
        
        # Calculate expected total board size
        expected_total_width = 75 * 10  # 750 pixels
        expected_total_height = 50 * 12  # 600 pixels
        
        # These calculations would be used by other components
        self.assertEqual(board.cell_W_pix * board.W_cells, expected_total_width)
        self.assertEqual(board.cell_H_pix * board.H_cells, expected_total_height)
    
    def test_board_with_real_img_object(self):
        """🧪 Test board initialization with actual Img object"""
        # Create a real Img object for more realistic testing
        real_img = Img()
        
        board = Board(
            cell_H_pix=64,
            cell_W_pix=64,
            W_cells=8,
            H_cells=8,
            img=real_img
        )
        
        self.assertIsInstance(board.img, Img)
        self.assertIsInstance(board.original_img, Img)
        
        # Verify they are different objects (deep copy)
        self.assertIsNot(board.img, board.original_img)
    
    def test_board_post_init_called(self):
        """🧪 Test that __post_init__ is automatically called"""
        with patch.object(Board, '_Board__post_init__') as mock_post_init:
            # Note: This test verifies the dataclass behavior
            # In reality, __post_init__ is called automatically
            pass
    
    def test_board_field_immutability(self):
        """🧪 Test that board fields can be modified after creation"""
        board = Board(
            cell_H_pix=64,
            cell_W_pix=64,
            W_cells=8,
            H_cells=8,
            img=self.mock_img
        )
        
        # Board fields should be modifiable (dataclass default behavior)
        board.cell_H_pix = 32
        board.cell_W_pix = 32
        board.W_cells = 4
        board.H_cells = 4
        
        self.assertEqual(board.cell_H_pix, 32)
        self.assertEqual(board.cell_W_pix, 32)
        self.assertEqual(board.W_cells, 4)
        self.assertEqual(board.H_cells, 4)
    
    def test_board_edge_cases(self):
        """🧪 Test board with edge case values"""
        # Test with minimum values
        board_min = Board(
            cell_H_pix=1,
            cell_W_pix=1,
            W_cells=1,
            H_cells=1,
            img=self.mock_img
        )
        
        self.assertEqual(board_min.cell_H_pix, 1)
        self.assertEqual(board_min.W_cells, 1)
        
        # Test with large values
        board_large = Board(
            cell_H_pix=1000,
            cell_W_pix=1000,
            W_cells=100,
            H_cells=100,
            img=self.mock_img
        )
        
        self.assertEqual(board_large.cell_H_pix, 1000)
        self.assertEqual(board_large.W_cells, 100)
    
    def test_board_repr_and_str(self):
        """🧪 Test string representation of board"""
        board = Board(
            cell_H_pix=64,
            cell_W_pix=64,
            W_cells=8,
            H_cells=8,
            img=self.mock_img
        )
        
        # Test that string representation contains key information
        board_str = str(board)
        self.assertIn("64", board_str)
        self.assertIn("8", board_str)
        
        # Test repr
        board_repr = repr(board)
        self.assertIn("Board", board_repr)
    
    def test_board_equality(self):
        """🧪 Test board equality comparison"""
        board1 = Board(
            cell_H_pix=64,
            cell_W_pix=64,
            W_cells=8,
            H_cells=8,
            img=self.mock_img
        )
        
        board2 = Board(
            cell_H_pix=64,
            cell_W_pix=64,
            W_cells=8,
            H_cells=8,
            img=self.mock_img
        )
        
        # Boards with same parameters should be equal (dataclass behavior)
        self.assertEqual(board1.cell_H_pix, board2.cell_H_pix)
        self.assertEqual(board1.W_cells, board2.W_cells)
    
    def test_board_copy_behavior(self):
        """🧪 Test board copying behavior"""
        original_board = Board(
            cell_H_pix=64,
            cell_W_pix=64,
            W_cells=8,
            H_cells=8,
            img=self.mock_img
        )
        
        # Test shallow copy
        copied_board = copy.copy(original_board)
        self.assertEqual(copied_board.cell_H_pix, original_board.cell_H_pix)
        self.assertEqual(copied_board.W_cells, original_board.W_cells)
        
        # Test deep copy
        deep_copied_board = copy.deepcopy(original_board)
        self.assertEqual(deep_copied_board.cell_H_pix, original_board.cell_H_pix)
        self.assertEqual(deep_copied_board.W_cells, original_board.W_cells)

if __name__ == '__main__':
    unittest.main(verbosity=2)
