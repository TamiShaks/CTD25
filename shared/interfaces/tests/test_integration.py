#!/usr/bin/env python3
"""
🧪 Integration Test for Kung Fu Chess
====================================

This test runs the main game functions to ensure everything works together.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

class TestIntegration(unittest.TestCase):
    """Integration test suite"""
    
    def test_game_main_function_exists(self):
        """🧪 Test that main game function exists and can be imported"""
        try:
            import main
            self.assertTrue(hasattr(main, 'main'))
            print("✅ Main game function import test passed!")
        except ImportError as e:
            self.fail(f"Failed to import main: {e}")
    
    def test_it1_interfaces_imports(self):
        """🧪 Test that It1_interfaces modules can be imported"""
        try:
            # Add the It1_interfaces directory to path
            it1_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            if it1_path not in sys.path:
                sys.path.insert(0, it1_path)
            
            # Test individual imports
            import img
            import Command
            
            self.assertTrue(hasattr(img, 'Img'))
            self.assertTrue(hasattr(Command, 'Command'))
            print("✅ It1_interfaces modules import test passed!")
            
        except ImportError as e:
            self.fail(f"Failed to import It1_interfaces modules: {e}")
    
    def test_pieces_directory_exists(self):
        """🧪 Test that pieces directory and board.csv exist"""
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        pieces_dir = os.path.join(project_root, 'pieces')
        board_csv = os.path.join(pieces_dir, 'board.csv')
        
        self.assertTrue(os.path.exists(pieces_dir), "Pieces directory should exist")
        self.assertTrue(os.path.exists(board_csv), "board.csv should exist")
        print("✅ Project structure test passed!")
    
    def test_board_image_exists(self):
        """🧪 Test that board.png exists"""
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        board_png = os.path.join(project_root, 'board.png')
        
        self.assertTrue(os.path.exists(board_png), "board.png should exist")
        print("✅ Board image test passed!")

if __name__ == '__main__':
    unittest.main(verbosity=2)
