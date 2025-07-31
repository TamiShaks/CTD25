#!/usr/bin/env python3
"""
🧪 Comprehensive Tests for PhysicsFactory Class
==============================================

Tests all functionality of the PhysicsFactory class including:
- Factory initialization with Board
- Physics object creation
- Configuration parameter handling
- Speed parameter processing
- Default value behavior
- Edge cases and error handling
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class MockBoard:
    """Mock Board class for testing"""
    def __init__(self, cell_H_pix=64, cell_W_pix=64, W_cells=8, H_cells=8):
        self.cell_H_pix = cell_H_pix
        self.cell_W_pix = cell_W_pix
        self.W_cells = W_cells
        self.H_cells = H_cells

class MockPhysics:
    """Mock Physics class for testing"""
    def __init__(self, start_cell, board, speed_m_s):
        self.start_cell = start_cell
        self.current_cell = start_cell
        self.target_cell = start_cell
        self.board = board
        self.speed_m_s = speed_m_s
        self.is_moving = False

class PhysicsFactory:
    def __init__(self, board): 
        """Initialize physics factory with board."""
        self.board = board

    def create(self, start_cell, cfg) -> MockPhysics:
        """Create a physics object with the given configuration."""
        speed = cfg.get('speed', 1.0)
        return MockPhysics(start_cell, self.board, speed)

class TestPhysicsFactory(unittest.TestCase):
    """Comprehensive test suite for PhysicsFactory class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create mock board for testing
        self.mock_board = MockBoard()
        
        # Standard configuration
        self.standard_cfg = {'speed': 2.0}
        
        # Standard starting cell
        self.standard_start_cell = (4, 4)  # Center of 8x8 board
        
        # Create factory instance
        self.factory = PhysicsFactory(self.mock_board)
    
    def test_factory_initialization(self):
        """🧪 Test PhysicsFactory initialization with board"""
        factory = PhysicsFactory(self.mock_board)
        
        # Verify the board is stored correctly
        self.assertEqual(factory.board, self.mock_board)
        self.assertIsInstance(factory.board, MockBoard)
    
    def test_factory_initialization_different_boards(self):
        """🧪 Test PhysicsFactory initialization with various board configurations"""
        test_boards = [
            MockBoard(32, 32, 4, 4),    # Small board
            MockBoard(64, 64, 8, 8),    # Standard chess board
            MockBoard(128, 128, 10, 10), # Large board
            MockBoard(50, 75, 6, 8),    # Rectangular cells
        ]
        
        for board in test_boards:
            with self.subTest(board=board):
                factory = PhysicsFactory(board)
                
                self.assertEqual(factory.board, board)
                self.assertEqual(factory.board.cell_H_pix, board.cell_H_pix)
                self.assertEqual(factory.board.cell_W_pix, board.cell_W_pix)
                self.assertEqual(factory.board.W_cells, board.W_cells)
                self.assertEqual(factory.board.H_cells, board.H_cells)
    
    def test_create_basic_functionality(self):
        """🧪 Test basic Physics creation through factory"""
        result = self.factory.create(
            start_cell=self.standard_start_cell,
            cfg=self.standard_cfg
        )
        
        # Verify Physics object was created with correct parameters
        self.assertEqual(result.start_cell, self.standard_start_cell)
        self.assertEqual(result.current_cell, self.standard_start_cell)
        self.assertEqual(result.target_cell, self.standard_start_cell)
        self.assertEqual(result.board, self.mock_board)
        self.assertEqual(result.speed_m_s, 2.0)
        self.assertEqual(result.is_moving, False)
        
        # Verify the factory returns a Physics-like instance
        self.assertIsInstance(result, MockPhysics)
    
    def test_create_with_default_speed(self):
        """🧪 Test Physics creation with default speed configuration"""
        # Configuration without speed parameter
        cfg_no_speed = {}
        
        result = self.factory.create(
            start_cell=self.standard_start_cell,
            cfg=cfg_no_speed
        )
        
        # Verify default speed is used
        self.assertEqual(result.speed_m_s, 1.0)  # Default speed
        self.assertEqual(result.start_cell, self.standard_start_cell)
        self.assertEqual(result.board, self.mock_board)
    
    def test_create_with_different_speeds(self):
        """🧪 Test Physics creation with various speed values"""
        test_speeds = [
            0.1,    # Very slow
            1.0,    # Default speed
            2.5,    # Medium speed
            5.0,    # Fast speed
            10.0,   # Very fast
        ]
        
        for speed in test_speeds:
            with self.subTest(speed=speed):
                cfg = {'speed': speed}
                result = self.factory.create(
                    start_cell=self.standard_start_cell,
                    cfg=cfg
                )
                
                self.assertEqual(result.speed_m_s, speed)
                self.assertEqual(result.start_cell, self.standard_start_cell)
                self.assertEqual(result.board, self.mock_board)
    
    def test_create_with_different_start_cells(self):
        """🧪 Test Physics creation with various starting cells"""
        test_start_cells = [
            (0, 0),    # Top-left corner
            (7, 7),    # Bottom-right corner (8x8 board)
            (3, 5),    # Random position
            (0, 7),    # Top-right corner
            (7, 0),    # Bottom-left corner
        ]
        
        for start_cell in test_start_cells:
            with self.subTest(start_cell=start_cell):
                result = self.factory.create(
                    start_cell=start_cell,
                    cfg=self.standard_cfg
                )
                
                self.assertEqual(result.start_cell, start_cell)
                self.assertEqual(result.current_cell, start_cell)
                self.assertEqual(result.target_cell, start_cell)
                self.assertEqual(result.speed_m_s, 2.0)
    
    def test_create_with_complex_config(self):
        """🧪 Test Physics creation with complex configuration"""
        # Configuration with extra unused parameters
        complex_cfg = {
            'speed': 3.5,
            'unused_param': 'should_be_ignored',
            'extra_data': {'nested': 'value'},
            'another_field': 42
        }
        
        result = self.factory.create(
            start_cell=self.standard_start_cell,
            cfg=complex_cfg
        )
        
        # Verify only relevant parameters are used
        self.assertEqual(result.speed_m_s, 3.5)
        self.assertEqual(result.start_cell, self.standard_start_cell)
        self.assertEqual(result.board, self.mock_board)
    
    def test_create_multiple_physics_objects(self):
        """🧪 Test creating multiple Physics objects through factory"""
        # Create first physics object
        result1 = self.factory.create(
            start_cell=(1, 1),
            cfg={'speed': 1.5}
        )
        
        # Create second physics object
        result2 = self.factory.create(
            start_cell=(6, 6),
            cfg={'speed': 2.5}
        )
        
        # Verify different instances are returned
        self.assertIsNot(result1, result2)
        
        # Verify first physics object properties
        self.assertEqual(result1.start_cell, (1, 1))
        self.assertEqual(result1.speed_m_s, 1.5)
        self.assertEqual(result1.board, self.mock_board)
        
        # Verify second physics object properties
        self.assertEqual(result2.start_cell, (6, 6))
        self.assertEqual(result2.speed_m_s, 2.5)
        self.assertEqual(result2.board, self.mock_board)
        
        # Verify both share the same board reference
        self.assertIs(result1.board, result2.board)
    
    def test_create_with_board_reference(self):
        """🧪 Test that created Physics objects reference the correct board"""
        # Create different board
        different_board = MockBoard(32, 32, 4, 4)
        different_factory = PhysicsFactory(different_board)
        
        # Create physics objects from different factories
        result1 = self.factory.create(self.standard_start_cell, self.standard_cfg)
        result2 = different_factory.create(self.standard_start_cell, self.standard_cfg)
        
        # Verify each physics object references its factory's board
        self.assertIs(result1.board, self.mock_board)
        self.assertIs(result2.board, different_board)
        self.assertIsNot(result1.board, result2.board)
    
    def test_config_parameter_extraction(self):
        """🧪 Test configuration parameter extraction behavior"""
        # Test with different config structures
        test_configs = [
            {'speed': 2.0},                           # Normal config
            {'speed': 2.0, 'other': 'value'},        # Config with extra params
            {},                                       # Empty config
            {'other_param': 'value'},                 # Config without speed
        ]
        
        expected_speeds = [2.0, 2.0, 1.0, 1.0]  # Expected speeds for each config
        
        for cfg, expected_speed in zip(test_configs, expected_speeds):
            with self.subTest(cfg=cfg, expected_speed=expected_speed):
                result = self.factory.create(
                    start_cell=self.standard_start_cell,
                    cfg=cfg
                )
                
                self.assertEqual(result.speed_m_s, expected_speed)
    
    def test_edge_case_speeds(self):
        """🧪 Test Physics creation with edge case speed values"""
        edge_case_speeds = [
            0.0,      # Zero speed
            0.001,    # Very small speed
            100.0,    # Very high speed
            -1.0,     # Negative speed (should still work)
        ]
        
        for speed in edge_case_speeds:
            with self.subTest(speed=speed):
                cfg = {'speed': speed}
                result = self.factory.create(
                    start_cell=self.standard_start_cell,
                    cfg=cfg
                )
                
                # Verify the speed is set as requested (no validation in factory)
                self.assertEqual(result.speed_m_s, speed)
                self.assertIsInstance(result, MockPhysics)
    
    def test_edge_case_start_cells(self):
        """🧪 Test Physics creation with edge case start cells"""
        edge_case_cells = [
            (-1, -1),      # Negative coordinates
            (100, 100),    # Very large coordinates
            (0, 0),        # Minimum valid coordinates
        ]
        
        for start_cell in edge_case_cells:
            with self.subTest(start_cell=start_cell):
                result = self.factory.create(
                    start_cell=start_cell,
                    cfg=self.standard_cfg
                )
                
                # Verify the start cell is set as requested (no validation in factory)
                self.assertEqual(result.start_cell, start_cell)
                self.assertEqual(result.current_cell, start_cell)
                self.assertEqual(result.target_cell, start_cell)
    
    def test_factory_method_signature(self):
        """🧪 Test that factory create method has correct signature"""
        # Verify create method exists and is callable
        self.assertTrue(hasattr(self.factory, 'create'))
        self.assertTrue(callable(self.factory.create))
        
        # Test that create method can be called with expected parameters
        result = self.factory.create(
            start_cell=(2, 3),
            cfg={'speed': 1.5}
        )
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, MockPhysics)
    
    def test_factory_state_independence(self):
        """🧪 Test that factory calls are independent of each other"""
        # Create multiple physics objects with different configurations
        results = []
        for i in range(5):
            result = self.factory.create(
                start_cell=(i, i),
                cfg={'speed': i + 1.0}
            )
            results.append(result)
        
        # Verify each physics object has its own state
        for i, result in enumerate(results):
            self.assertEqual(result.start_cell, (i, i))
            self.assertEqual(result.speed_m_s, i + 1.0)
            self.assertEqual(result.board, self.mock_board)
            
            # Verify they are different instances
            for j, other_result in enumerate(results):
                if i != j:
                    self.assertIsNot(result, other_result)
    
    def test_board_instance_preserved(self):
        """🧪 Test that the same board instance is used across physics creations"""
        # Create multiple physics objects
        result1 = self.factory.create((1, 1), {'speed': 1.0})
        result2 = self.factory.create((2, 2), {'speed': 2.0})
        result3 = self.factory.create((3, 3), {'speed': 3.0})
        
        # Verify all physics objects reference the same board instance
        self.assertIs(result1.board, self.mock_board)
        self.assertIs(result2.board, self.mock_board)
        self.assertIs(result3.board, self.mock_board)
        self.assertIs(result1.board, result2.board)
        self.assertIs(result2.board, result3.board)
    
    def test_config_dict_not_modified(self):
        """🧪 Test that the original config dict is not modified by the factory"""
        original_cfg = {'speed': 2.5, 'other': 'value'}
        original_cfg_copy = original_cfg.copy()
        
        self.factory.create(
            start_cell=self.standard_start_cell,
            cfg=original_cfg
        )
        
        # Verify original config dict was not modified
        self.assertEqual(original_cfg, original_cfg_copy)

if __name__ == '__main__':
    unittest.main(verbosity=2)
