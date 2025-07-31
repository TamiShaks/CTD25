#!/usr/bin/env python3
"""
🧪 Comprehensive Tests for State Class
=====================================

Tests all functionality of the State class including:
- Initialization and configuration
- State transitions
- Command handling
- Time-based updates
- Rest state functionality
- Deep copy operations
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import modules without relative imports
from State import State, create_long_rest_state, create_short_rest_state, create_move_state
from Command import Command
from Moves import Moves
from Graphics import Graphics  
from Physics import Physics

class TestState(unittest.TestCase):
    """Comprehensive test suite for State class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create mock objects for dependencies
        self.mock_moves = Mock(spec=Moves)
        self.mock_graphics = Mock(spec=Graphics)
        self.mock_graphics.state_name = "idle"
        self.mock_graphics.sprites_folder = "pieces/PW/states/idle/sprites"
        self.mock_graphics.cell_size = 64
        self.mock_graphics.copy.return_value = self.mock_graphics
        
        self.mock_physics = Mock(spec=Physics)
        self.mock_physics.current_cell = [0, 0]
        self.mock_physics.target_cell = [1, 1]
        self.mock_physics.is_moving = False
        self.mock_physics.copy.return_value = self.mock_physics
        
        # Create test command
        self.test_command = Command(
            timestamp=int(time.time() * 1000),
            player_id="player1",
            cmd_type="move",
            args=["a1", "a2"]
        )
        
    def test_state_initialization_basic(self):
        """🧪 Test basic state initialization"""
        state = State(
            moves=self.mock_moves,
            graphics=self.mock_graphics,
            physics=self.mock_physics,
            state_name="idle"
        )
        
        # Verify all parameters are stored correctly
        self.assertEqual(state.moves, self.mock_moves)
        self.assertEqual(state.graphics, self.mock_graphics)
        self.assertEqual(state.physics, self.mock_physics)
        self.assertEqual(state.state, "idle")
        self.assertEqual(state.transitions, {})
        self.assertFalse(state.is_rest_state)
        self.assertEqual(state.rest_duration_ms, 0)
        
    def test_state_initialization_different_names(self):
        """🧪 Test state initialization with different state names"""
        state_names = ["idle", "move", "attack", "rest", "long_rest"]
        
        for state_name in state_names:
            with self.subTest(state_name=state_name):
                state = State(
                    moves=self.mock_moves,
                    graphics=self.mock_graphics,
                    physics=self.mock_physics,
                    state_name=state_name
                )
                self.assertEqual(state.state, state_name)
    
    def test_set_transition(self):
        """🧪 Test setting state transitions"""
        state1 = State(self.mock_moves, self.mock_graphics, self.mock_physics, "idle")
        state2 = State(self.mock_moves, self.mock_graphics, self.mock_physics, "move")
        
        # Set transition
        state1.set_transition("move_command", state2)
        
        # Verify transition is set
        self.assertIn("move_command", state1.transitions)
        self.assertEqual(state1.transitions["move_command"], state2)
    
    def test_multiple_transitions(self):
        """🧪 Test setting multiple transitions"""
        idle_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "idle")
        move_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "move")
        attack_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "attack")
        
        # Set multiple transitions
        idle_state.set_transition("move", move_state)
        idle_state.set_transition("attack", attack_state)
        
        # Verify all transitions
        self.assertEqual(len(idle_state.transitions), 2)
        self.assertEqual(idle_state.transitions["move"], move_state)
        self.assertEqual(idle_state.transitions["attack"], attack_state)
    
    def test_state_reset(self):
        """🧪 Test state reset functionality"""
        state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "idle")
        
        # Reset with command
        state.reset(self.test_command)
        
        # Verify reset behavior
        self.assertEqual(state.current_command, self.test_command)
        self.assertEqual(state.state_start_time, self.test_command.timestamp)
        self.mock_graphics.reset.assert_called_once_with(self.test_command)
        self.mock_physics.reset.assert_called_once_with(self.test_command)
    
    def test_can_transition_non_rest_state(self):
        """🧪 Test can_transition for non-rest states"""
        state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "idle")
        
        # Non-rest states should always be able to transition
        current_time = int(time.time() * 1000)
        self.assertTrue(state.can_transition(current_time))
    
    def test_can_transition_rest_state(self):
        """🧪 Test can_transition for rest states"""
        state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "rest")
        state.is_rest_state = True
        state.rest_duration_ms = 1000  # 1 second
        
        current_time = int(time.time() * 1000)
        state.state_start_time = current_time
        
        # Should not be able to transition immediately
        self.assertFalse(state.can_transition(current_time))
        
        # Should be able to transition after rest duration
        future_time = current_time + 1500  # 1.5 seconds later
        self.assertTrue(state.can_transition(future_time))
    
    @patch('State.GraphicsFactory')
    def test_state_copy(self, mock_graphics_factory):
        """🧪 Test state deep copy functionality"""
        # Setup mock graphics factory
        mock_new_graphics = Mock()
        mock_graphics_factory.create.return_value = mock_new_graphics
        
        original_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "idle")
        original_state.is_rest_state = True
        original_state.rest_duration_ms = 2000
        
        # Create copy
        copied_state = original_state.copy()
        
        # Verify copy has same properties but different objects
        self.assertEqual(copied_state.state, original_state.state)
        self.assertEqual(copied_state.is_rest_state, original_state.is_rest_state)
        self.assertEqual(copied_state.rest_duration_ms, original_state.rest_duration_ms)
        self.assertEqual(copied_state.moves, original_state.moves)  # Same moves object
        
        # Verify graphics and physics are copied
        self.mock_graphics.copy.assert_called_once()
        self.mock_physics.copy.assert_called_once()
    
    def test_get_command(self):
        """🧪 Test getting current command"""
        state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "idle")
        
        # Initially no command
        self.assertIsNone(state.get_command())
        
        # After reset, should return the command
        state.reset(self.test_command)
        self.assertEqual(state.get_command(), self.test_command)
    
    @patch('State.GraphicsFactory')
    def test_get_state_after_command_with_transition(self, mock_graphics_factory):
        """🧪 Test getting next state after command with valid transition"""
        mock_new_graphics = Mock()
        mock_graphics_factory.create.return_value = mock_new_graphics
        
        idle_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "idle")
        move_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "move")
        
        # Set up transition
        idle_state.set_transition("move", move_state)
        
        # Test transition
        current_time = int(time.time() * 1000)
        move_command = Command(current_time, "player1", "move", ["a1", "a2"])
        
        next_state = idle_state.get_state_after_command(move_command, current_time)
        
        # Should return a new state instance (not the template)
        self.assertIsNotNone(next_state)
        self.assertNotEqual(next_state, idle_state)
        self.assertEqual(next_state.state, "move")
    
    def test_get_state_after_command_no_transition(self):
        """🧪 Test getting next state after command with no valid transition"""
        state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "idle")
        
        # No transitions set up
        current_time = int(time.time() * 1000)
        unknown_command = Command(current_time, "player1", "unknown", [])
        
        next_state = state.get_state_after_command(unknown_command, current_time)
        
        # Should return the same state
        self.assertEqual(next_state, state)
    
    def test_get_state_after_command_cannot_transition(self):
        """🧪 Test getting next state when can't transition (rest state)"""
        state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "rest")
        state.is_rest_state = True
        state.rest_duration_ms = 1000
        
        current_time = int(time.time() * 1000)
        state.state_start_time = current_time
        
        move_command = Command(current_time, "player1", "move", [])
        next_state = state.get_state_after_command(move_command, current_time)
        
        # Should return the same state (can't transition yet)
        self.assertEqual(next_state, state)
    
    def test_update_graphics_and_physics(self):
        """🧪 Test state update calls graphics and physics update"""
        state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "idle")
        
        current_time = int(time.time() * 1000)
        self.mock_physics.update.return_value = False  # Movement not complete
        
        result_state = state.update(current_time)
        
        # Verify update methods were called
        self.mock_graphics.update.assert_called_once_with(current_time)
        self.mock_physics.update.assert_called_once_with(current_time)
        
        # Should return the same state
        self.assertEqual(result_state, state)

class TestStateHelperFunctions(unittest.TestCase):
    """Test helper functions for creating special states"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_moves = Mock(spec=Moves)
        self.mock_graphics = Mock(spec=Graphics)
        self.mock_physics = Mock(spec=Physics)
        
        self.idle_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "idle")
    
    def test_create_long_rest_state(self):
        """🧪 Test creating long rest state"""
        rest_state = create_long_rest_state(
            self.idle_state, self.mock_moves, self.mock_graphics, self.mock_physics
        )
        
        # Verify rest state properties
        self.assertEqual(rest_state.state, "long_rest")
        self.assertTrue(rest_state.is_rest_state)
        self.assertEqual(rest_state.rest_duration_ms, 2000)  # 2 seconds
        
        # Verify transition back to idle
        self.assertIn("timeout", rest_state.transitions)
        self.assertEqual(rest_state.transitions["timeout"], self.idle_state)
    
    def test_create_short_rest_state(self):
        """🧪 Test creating short rest state"""
        rest_state = create_short_rest_state(
            self.idle_state, self.mock_moves, self.mock_graphics, self.mock_physics
        )
        
        # Verify rest state properties
        self.assertEqual(rest_state.state, "short_rest")
        self.assertTrue(rest_state.is_rest_state)
        self.assertEqual(rest_state.rest_duration_ms, 1000)  # 1 second
        
        # Verify transition back to idle
        self.assertIn("timeout", rest_state.transitions)
        self.assertEqual(rest_state.transitions["timeout"], self.idle_state)
    
    @patch('It1_interfaces.State.create_long_rest_state')
    def test_create_move_state(self, mock_create_long_rest):
        """🧪 Test creating move state"""
        mock_long_rest = Mock()
        mock_create_long_rest.return_value = mock_long_rest
        
        move_state = create_move_state(
            self.idle_state, self.mock_moves, self.mock_graphics, self.mock_physics
        )
        
        # Verify move state properties
        self.assertEqual(move_state.state, "move")
        self.assertFalse(move_state.is_rest_state)
        
        # Verify transition to long rest on completion
        self.assertIn("complete", move_state.transitions)
        self.assertEqual(move_state.transitions["complete"], mock_long_rest)
        
        # Verify long rest state was created with correct parameters
        mock_create_long_rest.assert_called_once_with(
            self.idle_state, self.mock_moves, self.mock_graphics, self.mock_physics
        )

if __name__ == '__main__':
    unittest.main(verbosity=2)
