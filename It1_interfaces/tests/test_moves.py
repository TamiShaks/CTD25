#!/usr/bin/env python3
"""
🧪 Simple Test for Moves Class
"""

import unittest
import sys
import os
import tempfile
import pathlib

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Moves import Moves

class TestMoves(unittest.TestCase):
    """Simple test suite for Moves class"""
    
    def test_moves_initialization_with_nonexistent_file(self):
        """🧪 Test moves initialization with non-existent file"""
        fake_path = pathlib.Path("nonexistent_moves.txt")
        moves = Moves(fake_path, dims=(8, 8))
        
        self.assertEqual(moves.board_height, 8)
        self.assertEqual(moves.board_width, 8)
        self.assertEqual(moves.move_deltas, [])  # Should be empty for non-existent file
        print("✅ Moves initialization with non-existent file test passed!")
    
    def test_moves_initialization_with_simple_moves(self):
        """🧪 Test moves initialization with a simple moves file"""
        # Create a temporary file with simple moves
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as f:
            f.write("-1,0\n")  # Up
            f.write("1,0\n")   # Down
            f.write("0,-1\n")  # Left
            f.write("0,1\n")   # Right
            temp_path = pathlib.Path(f.name)
        
        try:
            moves = Moves(temp_path, dims=(8, 8))
            
            self.assertEqual(moves.board_height, 8)
            self.assertEqual(moves.board_width, 8)
            
            expected_moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            self.assertEqual(moves.move_deltas, expected_moves)
            print("✅ Moves initialization with simple moves test passed!")
            
        finally:
            # Clean up temporary file
            temp_path.unlink()
    
    def test_get_valid_moves_from_position(self):
        """🧪 Test getting valid moves from a specific position"""
        # Create moves with basic directional moves
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as f:
            f.write("-1,0\n")  # Up
            f.write("1,0\n")   # Down
            f.write("0,-1\n")  # Left
            f.write("0,1\n")   # Right
            temp_path = pathlib.Path(f.name)
        
        try:
            moves = Moves(temp_path, dims=(8, 8))
            
            # Test from center position (should have all moves available)
            valid_moves = moves.get_moves(3, 3)
            expected_positions = [(2, 3), (4, 3), (3, 2), (3, 4)]
            self.assertEqual(set(valid_moves), set(expected_positions))
            
            # Test from corner position (should filter out-of-bounds moves)
            valid_moves_corner = moves.get_moves(0, 0)
            expected_corner = [(1, 0), (0, 1)]  # Only down and right
            self.assertEqual(set(valid_moves_corner), set(expected_corner))
            
            print("✅ Get valid moves test passed!")
            
        finally:
            # Clean up temporary file
            temp_path.unlink()
    
    def test_different_board_dimensions(self):
        """🧪 Test with different board dimensions"""
        fake_path = pathlib.Path("fake.txt")
        
        # Test different board sizes
        test_dimensions = [
            (4, 4),
            (6, 8),
            (10, 12),
        ]
        
        for height, width in test_dimensions:
            with self.subTest(height=height, width=width):
                moves = Moves(fake_path, dims=(height, width))
                self.assertEqual(moves.board_height, height)
                self.assertEqual(moves.board_width, width)
        
        print("✅ Different board dimensions test passed!")

if __name__ == '__main__':
    unittest.main(verbosity=2)
