#!/usr/bin/env python3
"""
🧪 Comprehensive Tests for Physics Class
=======================================

Tests all functionality of the Physics class including:
- Initialization and configuration
- Movement calculations
- Position interpolation
- Command handling (Move, Jump)
- Timing and speed calculations
- Copy functionality
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import modules without relative imports
from Physics import Physics
from Command import Command
from Board import Board

class TestPhysics(unittest.TestCase):
    """Comprehensive test suite for Physics class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create mock board
        self.mock_board = Mock(spec=Board)
        self.mock_board.cell_H_pix = 64
        self.mock_board.cell_W_pix = 64
        
        # Standard starting position
        self.start_cell = (2, 2)  # Middle of a small board
        self.current_time = int(time.time() * 1000)
        
    def test_physics_initialization(self):
        """🧪 Test basic physics initialization"""
        physics = Physics(
            start_cell=self.start_cell,
            board=self.mock_board,
            speed_m_s=1.0
        )
        
        # Verify initialization
        self.assertEqual(physics.start_cell, self.start_cell)
        self.assertEqual(physics.current_cell, self.start_cell)
        self.assertEqual(physics.target_cell, self.start_cell)
        self.assertEqual(physics.board, self.mock_board)
        self.assertEqual(physics.speed_m_s, 1.0)
        self.assertFalse(physics.is_moving)
        self.assertEqual(physics.move_start_time, 0)
        self.assertEqual(physics.move_duration, 0)
    
    def test_physics_initialization_different_speeds(self):
        """🧪 Test physics initialization with different speeds"""
        speeds = [0.5, 1.0, 2.0, 5.0]
        
        for speed in speeds:
            with self.subTest(speed=speed):
                physics = Physics(self.start_cell, self.mock_board, speed)
                self.assertEqual(physics.speed_m_s, speed)
    
    def test_physics_initialization_different_positions(self):
        """🧪 Test physics initialization with different starting positions"""
        positions = [(0, 0), (1, 1), (3, 5), (7, 7)]
        
        for pos in positions:
            with self.subTest(position=pos):
                physics = Physics(pos, self.mock_board, 1.0)
                self.assertEqual(physics.start_cell, pos)
                self.assertEqual(physics.current_cell, pos)
                self.assertEqual(physics.target_cell, pos)
    
    def test_physics_copy(self):
        """🧪 Test physics copy functionality"""
        original = Physics(self.start_cell, self.mock_board, 2.0)
        original.current_cell = (3, 3)
        original.target_cell = (4, 4)
        original.is_moving = True
        original.move_start_time = self.current_time
        original.move_duration = 1000
        
        # Create copy
        copied = original.copy()
        
        # Verify copy has same values but is different object
        self.assertIsNot(copied, original)
        self.assertEqual(copied.start_cell, original.start_cell)
        self.assertEqual(copied.current_cell, original.current_cell)
        self.assertEqual(copied.target_cell, original.target_cell)
        self.assertEqual(copied.board, original.board)
        self.assertEqual(copied.speed_m_s, original.speed_m_s)
        self.assertEqual(copied.is_moving, original.is_moving)
        self.assertEqual(copied.move_start_time, original.move_start_time)
        self.assertEqual(copied.move_duration, original.move_duration)
    
    def test_reset_with_move_command(self):
        """🧪 Test reset with move command"""
        physics = Physics(self.start_cell, self.mock_board, 1.0)
        
        # Create move command
        target_cell = (4, 4)
        move_command = Command(
            timestamp=self.current_time,
            player_id="player1",
            cmd_type="Move",
            args=["PW1", "c3", "e5"]
        )
        move_command.params = [self.start_cell, target_cell]
        
        physics.reset(move_command)
        
        # Verify move setup
        self.assertEqual(physics.target_cell, target_cell)
        self.assertTrue(physics.is_moving)
        self.assertEqual(physics.move_start_time, self.current_time)
        
        # Verify duration calculation (distance = 2, speed = 4 cells/sec, so 500ms)
        expected_duration = int(2 / Physics.SLIDE_CELLS_PER_SEC * 1000)
        self.assertEqual(physics.move_duration, expected_duration)
    
    def test_reset_with_jump_command(self):
        """🧪 Test reset with jump command"""
        physics = Physics(self.start_cell, self.mock_board, 1.0)
        
        # Create jump command
        jump_command = Command(
            timestamp=self.current_time,
            player_id="player1",
            cmd_type="Jump",
            args=["PW1", "c3", "e5"]
        )
        jump_command.params = [self.start_cell, (4, 4)]
        
        physics.reset(jump_command)
        
        # Verify jump setup (stays in same position)
        self.assertEqual(physics.target_cell, self.start_cell)
        self.assertTrue(physics.is_moving)
        self.assertEqual(physics.move_start_time, self.current_time)
        self.assertEqual(physics.move_duration, 1500)  # Fixed 1.5 seconds for jump
    
    def test_reset_with_other_command(self):
        """🧪 Test reset with non-movement command"""
        physics = Physics(self.start_cell, self.mock_board, 1.0)
        physics.is_moving = True  # Set to moving initially
        
        # Create non-movement command
        other_command = Command(
            timestamp=self.current_time,
            player_id="player1",
            cmd_type="Attack",
            args=["PW1"]
        )
        
        physics.reset(other_command)
        
        # Should stop movement
        self.assertFalse(physics.is_moving)
    
    def test_get_pos_not_moving(self):
        """🧪 Test get_pos when not moving"""
        physics = Physics(self.start_cell, self.mock_board, 1.0)
        
        x, y = physics.get_pos(self.current_time)
        
        # Should return current cell position in pixels
        expected_x = self.start_cell[1] * self.mock_board.cell_W_pix
        expected_y = self.start_cell[0] * self.mock_board.cell_H_pix
        self.assertEqual(x, expected_x)
        self.assertEqual(y, expected_y)
    
    def test_get_pos_moving_start(self):
        """🧪 Test get_pos at start of movement"""
        physics = Physics(self.start_cell, self.mock_board, 1.0)
        
        # Set up movement from (2,2) to (4,4)
        physics.current_cell = (2, 2)
        physics.target_cell = (4, 4)
        physics.is_moving = True
        physics.move_start_time = self.current_time
        physics.move_duration = 1000
        
        # Get position at start of movement
        x, y = physics.get_pos(self.current_time)
        
        # Should be at starting position
        expected_x = 2 * self.mock_board.cell_W_pix
        expected_y = 2 * self.mock_board.cell_H_pix
        self.assertEqual(x, expected_x)
        self.assertEqual(y, expected_y)
    
    def test_get_pos_moving_middle(self):
        """🧪 Test get_pos in middle of movement"""
        physics = Physics(self.start_cell, self.mock_board, 1.0)
        
        # Set up movement from (2,2) to (4,4)
        physics.current_cell = (2, 2)
        physics.target_cell = (4, 4)
        physics.is_moving = True
        physics.move_start_time = self.current_time
        physics.move_duration = 1000
        
        # Get position halfway through movement
        halfway_time = self.current_time + 500
        x, y = physics.get_pos(halfway_time)
        
        # Should be halfway between start and target
        expected_x = 3 * self.mock_board.cell_W_pix  # Halfway between 2 and 4
        expected_y = 3 * self.mock_board.cell_H_pix
        self.assertEqual(x, expected_x)
        self.assertEqual(y, expected_y)
    
    def test_get_pos_moving_end(self):
        """🧪 Test get_pos at end of movement"""
        physics = Physics(self.start_cell, self.mock_board, 1.0)
        
        # Set up movement from (2,2) to (4,4)
        physics.current_cell = (2, 2)
        physics.target_cell = (4, 4)
        physics.is_moving = True
        physics.move_start_time = self.current_time
        physics.move_duration = 1000
        
        # Get position at end of movement
        end_time = self.current_time + 1000
        x, y = physics.get_pos(end_time)
        
        # Should be at target position
        expected_x = 4 * self.mock_board.cell_W_pix
        expected_y = 4 * self.mock_board.cell_H_pix
        self.assertEqual(x, expected_x)
        self.assertEqual(y, expected_y)
    
    def test_get_pos_moving_past_end(self):
        """🧪 Test get_pos past end of movement"""
        physics = Physics(self.start_cell, self.mock_board, 1.0)
        
        # Set up movement from (2,2) to (4,4)
        physics.current_cell = (2, 2)
        physics.target_cell = (4, 4)
        physics.is_moving = True
        physics.move_start_time = self.current_time
        physics.move_duration = 1000
        
        # Get position well past end of movement
        past_end_time = self.current_time + 2000
        x, y = physics.get_pos(past_end_time)
        
        # Should still be at target position
        expected_x = 4 * self.mock_board.cell_W_pix
        expected_y = 4 * self.mock_board.cell_H_pix
        self.assertEqual(x, expected_x)
        self.assertEqual(y, expected_y)
    
    def test_update_movement_in_progress(self):
        """🧪 Test update during movement"""
        physics = Physics(self.start_cell, self.mock_board, 1.0)
        
        # Set up movement
        physics.current_cell = (2, 2)
        physics.target_cell = (4, 4)
        physics.is_moving = True
        physics.move_start_time = self.current_time
        physics.move_duration = 1000
        
        # Update during movement
        middle_time = self.current_time + 500
        movement_complete = physics.update(middle_time)
        
        # Movement should not be complete
        self.assertFalse(movement_complete)
        self.assertTrue(physics.is_moving)
        self.assertEqual(physics.current_cell, (2, 2))  # Current cell unchanged during movement
    
    def test_update_movement_complete(self):
        """🧪 Test update when movement completes"""
        physics = Physics(self.start_cell, self.mock_board, 1.0)
        
        # Set up movement
        physics.current_cell = (2, 2)
        physics.target_cell = (4, 4)
        physics.is_moving = True
        physics.move_start_time = self.current_time
        physics.move_duration = 1000
        
        # Update at end of movement
        end_time = self.current_time + 1000
        movement_complete = physics.update(end_time)
        
        # Movement should be complete
        self.assertTrue(movement_complete)
        self.assertFalse(physics.is_moving)
        self.assertEqual(physics.current_cell, (4, 4))  # Current cell updated to target
    
    def test_update_not_moving(self):
        """🧪 Test update when not moving"""
        physics = Physics(self.start_cell, self.mock_board, 1.0)
        
        # Update when not moving
        movement_complete = physics.update(self.current_time)
        
        # Should return False (no movement to complete)
        self.assertFalse(movement_complete)
        self.assertFalse(physics.is_moving)
    
    def test_movement_duration_calculation(self):
        """🧪 Test movement duration calculation for different distances"""
        physics = Physics(self.start_cell, self.mock_board, 1.0)
        
        test_cases = [
            ((0, 0), (1, 0), 1),  # 1 cell horizontal
            ((0, 0), (0, 1), 1),  # 1 cell vertical  
            ((0, 0), (1, 1), 1),  # 1 cell diagonal
            ((0, 0), (2, 0), 2),  # 2 cells horizontal
            ((0, 0), (2, 2), 2),  # 2 cells diagonal
            ((0, 0), (3, 4), 4),  # Knight move (max distance)
        ]
        
        for start, target, expected_distance in test_cases:
            with self.subTest(start=start, target=target):
                command = Command(self.current_time, "player1", "Move", [])
                command.params = [start, target]
                
                physics.current_cell = start
                physics.reset(command)
                
                expected_duration = int(expected_distance / Physics.SLIDE_CELLS_PER_SEC * 1000)
                self.assertEqual(physics.move_duration, expected_duration)
    
    def test_slide_speed_constant(self):
        """🧪 Test that slide speed constant is reasonable"""
        # Should be a positive number representing cells per second
        self.assertGreater(Physics.SLIDE_CELLS_PER_SEC, 0)
        self.assertIsInstance(Physics.SLIDE_CELLS_PER_SEC, float)

if __name__ == '__main__':
    unittest.main(verbosity=2)
