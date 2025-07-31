#!/usr/bin/env python3
"""
🧪 Compact Test Example - PhysicsFactory Short Version
===================================================

Shorter, grouped tests for PhysicsFactory functionality.
"""

import unittest
import sys
import os
import pathlib

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class MockBoard:
    def __init__(self, cell_H_pix=64, cell_W_pix=64, W_cells=8, H_cells=8):
        self.cell_H_pix = cell_H_pix
        self.cell_W_pix = cell_W_pix
        self.W_cells = W_cells
        self.H_cells = H_cells

class MockPhysics:
    def __init__(self, start_cell, board, speed_m_s):
        self.start_cell = start_cell
        self.current_cell = start_cell
        self.target_cell = start_cell
        self.board = board
        self.speed_m_s = speed_m_s
        self.is_moving = False

class PhysicsFactory:
    def __init__(self, board): 
        self.board = board

    def create(self, start_cell, cfg) -> MockPhysics:
        speed = cfg.get('speed', 1.0)
        return MockPhysics(start_cell, self.board, speed)

class TestPhysicsFactoryCompact(unittest.TestCase):
    """Compact test suite for PhysicsFactory - fewer, grouped tests"""
    
    def setUp(self):
        self.board = MockBoard()
        self.factory = PhysicsFactory(self.board)
    
    def test_factory_initialization_and_basic_creation(self):
        """🧪 Test factory initialization and basic physics creation"""
        # Test initialization
        self.assertEqual(self.factory.board, self.board)
        
        # Test basic creation
        result = self.factory.create((4, 4), {'speed': 2.0})
        self.assertEqual(result.start_cell, (4, 4))
        self.assertEqual(result.speed_m_s, 2.0)
        self.assertEqual(result.board, self.board)
        self.assertIsInstance(result, MockPhysics)
    
    def test_speed_configurations(self):
        """🧪 Test various speed configurations in one test"""
        test_cases = [
            ({}, 1.0),                    # Default speed
            ({'speed': 2.5}, 2.5),        # Custom speed
            ({'speed': 0.1}, 0.1),        # Very slow
            ({'speed': 100.0}, 100.0),    # Very fast
            ({'other': 'value'}, 1.0),    # No speed param
        ]
        
        for cfg, expected_speed in test_cases:
            with self.subTest(cfg=cfg):
                result = self.factory.create((0, 0), cfg)
                self.assertEqual(result.speed_m_s, expected_speed)
    
    def test_different_start_positions(self):
        """🧪 Test various starting positions in one test"""
        positions = [(0, 0), (7, 7), (3, 5), (-1, -1), (100, 100)]
        
        for pos in positions:
            with self.subTest(position=pos):
                result = self.factory.create(pos, {'speed': 1.0})
                self.assertEqual(result.start_cell, pos)
                self.assertEqual(result.current_cell, pos)
                self.assertEqual(result.target_cell, pos)
    
    def test_multiple_instances_and_independence(self):
        """🧪 Test multiple instance creation and independence"""
        # Create multiple instances
        instances = [
            self.factory.create((i, i), {'speed': float(i + 1)})
            for i in range(3)
        ]
        
        # Verify independence
        for i, instance in enumerate(instances):
            self.assertEqual(instance.start_cell, (i, i))
            self.assertEqual(instance.speed_m_s, float(i + 1))
            self.assertEqual(instance.board, self.board)
            
            # Verify different instances
            for j, other in enumerate(instances):
                if i != j:
                    self.assertIsNot(instance, other)

if __name__ == '__main__':
    unittest.main(verbosity=2)
