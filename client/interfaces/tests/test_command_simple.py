#!/usr/bin/env python3
"""
🧪 Simple Test for Command Class
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Command import Command

class TestCommand(unittest.TestCase):
    """Simple test suite for Command class"""
    
    def test_command_basic_initialization(self):
        """🧪 Test basic command initialization"""
        command = Command(
            timestamp=1000,
            piece_id="PW60",
            type="Move",
            params=[(0, 0), (0, 1)]
        )
        
        self.assertEqual(command.timestamp, 1000)
        self.assertEqual(command.piece_id, "PW60")
        self.assertEqual(command.type, "Move")
        self.assertEqual(command.params, [(0, 0), (0, 1)])
        print("✅ Command initialization test passed!")
    
    def test_create_move_command_factory(self):
        """🧪 Test the factory method for creating move commands"""
        move_command = Command.create_move_command(
            timestamp=1000,
            piece_id="PW60",
            from_cell=(2, 3),
            to_cell=(4, 5)
        )
        
        self.assertEqual(move_command.type, "Move")
        self.assertEqual(move_command.params, [(2, 3), (4, 5)])
        print("✅ Command factory test passed!")

if __name__ == '__main__':
    unittest.main(verbosity=2)
