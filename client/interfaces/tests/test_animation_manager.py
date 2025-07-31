"""
Comprehensive test suite for AnimationManager class.

Tests the animation system including:
- Animation manager initialization
- Event handling and game state management
- Animation lifecycle (add, update, cleanup)
- Time-based animation progression
- Event-driven state transitions
- Edge cases and error handling
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os
import time

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Add main project directory for imports
main_dir = os.path.dirname(parent_dir)
sys.path.insert(0, main_dir)

from AnimationManager import AnimationManager
from EventTypes import GAME_STARTED, GAME_ENDED


class TestAnimationManager(unittest.TestCase):
    """Test suite for AnimationManager class covering all animation functionality."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.animation_manager = AnimationManager()
        
        # Mock time.time for consistent testing
        self.time_patcher = patch('It1_interfaces.AnimationManager.time')
        self.mock_time = self.time_patcher.start()
        self.mock_time.time.return_value = 1000.0  # Fixed timestamp: 1000 seconds
        
        # Define test animation types
        self.FADE_IN = "fade_in"
        self.SLIDE_DOWN = "slide_down"
        self.BOUNCE = "bounce"
        self.EXPLOSION = "explosion"

    def tearDown(self):
        """Clean up after each test method."""
        self.time_patcher.stop()

    def test_animation_manager_initialization(self):
        """Test AnimationManager initialization."""
        manager = AnimationManager()
        
        self.assertIsInstance(manager, AnimationManager)
        self.assertEqual(manager.active_animations, [])
        self.assertEqual(manager.game_state, "waiting")
        self.assertIsInstance(manager.active_animations, list)

    def test_initial_state(self):
        """Test initial animation manager state."""
        self.assertEqual(self.animation_manager.game_state, "waiting")
        self.assertEqual(len(self.animation_manager.active_animations), 0)
        self.assertEqual(self.animation_manager.get_animation_count(), 0)

    def test_update_game_started_event(self):
        """Test handling GAME_STARTED event."""
        test_data = {"time": 1500, "players": ["Alice", "Bob"]}
        
        self.animation_manager.update(GAME_STARTED, test_data)
        
        # Verify state transition
        self.assertEqual(self.animation_manager.game_state, "playing")

    def test_update_game_ended_event(self):
        """Test handling GAME_ENDED event."""
        # First start the game
        self.animation_manager.update(GAME_STARTED, {"time": 1000})
        
        # Add some animations
        self.animation_manager.add_animation(self.FADE_IN, 500)
        self.animation_manager.add_animation(self.SLIDE_DOWN, 300)
        self.assertEqual(self.animation_manager.get_animation_count(), 2)
        
        # End the game
        test_data = {"time": 2000, "winner": "Alice"}
        self.animation_manager.update(GAME_ENDED, test_data)
        
        # Verify state transition and cleanup
        self.assertEqual(self.animation_manager.game_state, "ended")
        self.assertEqual(self.animation_manager.get_animation_count(), 0)

    def test_update_unknown_event(self):
        """Test handling unknown event types."""
        initial_state = self.animation_manager.game_state
        
        # Send unknown event
        self.animation_manager.update("UNKNOWN_EVENT", {"data": "test"})
        
        # State should remain unchanged
        self.assertEqual(self.animation_manager.game_state, initial_state)

    def test_update_with_none_data(self):
        """Test handling events with None data."""
        # Should not raise exception
        self.animation_manager.update(GAME_STARTED, None)
        
        self.assertEqual(self.animation_manager.game_state, "playing")

    def test_update_with_missing_time_data(self):
        """Test handling events with missing time data."""
        # Should not raise exception when time is missing
        self.animation_manager.update(GAME_STARTED, {"players": ["Alice"]})
        
        self.assertEqual(self.animation_manager.game_state, "playing")

    def test_add_animation_basic(self):
        """Test adding a basic animation."""
        self.animation_manager.add_animation(self.FADE_IN, 1000)
        
        self.assertEqual(self.animation_manager.get_animation_count(), 1)
        
        animation = self.animation_manager.active_animations[0]
        self.assertEqual(animation["type"], self.FADE_IN)
        self.assertEqual(animation["duration"], 1000)
        self.assertEqual(animation["start_time"], 1000000.0)  # 1000 * 1000
        self.assertIsNone(animation["target"])

    def test_add_animation_with_target(self):
        """Test adding animation with target object."""
        target_piece = Mock()
        target_piece.piece_id = "KW1"
        
        self.animation_manager.add_animation(self.BOUNCE, 500, target=target_piece)
        
        animation = self.animation_manager.active_animations[0]
        self.assertEqual(animation["type"], self.BOUNCE)
        self.assertEqual(animation["duration"], 500)
        self.assertEqual(animation["target"], target_piece)

    def test_add_multiple_animations(self):
        """Test adding multiple animations."""
        target1 = Mock()
        target2 = Mock()
        
        self.animation_manager.add_animation(self.FADE_IN, 1000, target=target1)
        self.animation_manager.add_animation(self.SLIDE_DOWN, 750, target=target2)
        self.animation_manager.add_animation(self.EXPLOSION, 200)
        
        self.assertEqual(self.animation_manager.get_animation_count(), 3)
        
        # Verify animation details
        animations = self.animation_manager.active_animations
        self.assertEqual(animations[0]["type"], self.FADE_IN)
        self.assertEqual(animations[1]["type"], self.SLIDE_DOWN)
        self.assertEqual(animations[2]["type"], self.EXPLOSION)

    def test_add_animation_zero_duration(self):
        """Test adding animation with zero duration."""
        self.animation_manager.add_animation(self.FADE_IN, 0)
        
        self.assertEqual(self.animation_manager.get_animation_count(), 1)
        self.assertEqual(self.animation_manager.active_animations[0]["duration"], 0)

    def test_add_animation_negative_duration(self):
        """Test adding animation with negative duration."""
        self.animation_manager.add_animation(self.FADE_IN, -100)
        
        self.assertEqual(self.animation_manager.get_animation_count(), 1)
        self.assertEqual(self.animation_manager.active_animations[0]["duration"], -100)

    def test_update_animations_no_animations(self):
        """Test updating animations when none are active."""
        current_time = 1001000.0  # 1001 seconds in ms
        
        # Should not raise exception
        self.animation_manager.update_animations(current_time)
        
        self.assertEqual(self.animation_manager.get_animation_count(), 0)

    def test_update_animations_not_completed(self):
        """Test updating animations that haven't completed yet."""
        # Add animations
        self.animation_manager.add_animation(self.FADE_IN, 2000)  # 2 second duration
        self.animation_manager.add_animation(self.SLIDE_DOWN, 1500)  # 1.5 second duration
        
        # Update with time before completion (0.5 seconds elapsed)
        current_time = 1000500.0  # 1000.5 seconds in ms
        self.animation_manager.update_animations(current_time)
        
        # Both animations should still be active
        self.assertEqual(self.animation_manager.get_animation_count(), 2)

    def test_update_animations_some_completed(self):
        """Test updating animations when some have completed."""
        # Add animations with different durations
        self.animation_manager.add_animation(self.FADE_IN, 800)    # 0.8 seconds
        self.animation_manager.add_animation(self.SLIDE_DOWN, 1200) # 1.2 seconds
        self.animation_manager.add_animation(self.BOUNCE, 500)     # 0.5 seconds
        
        # Update with time that completes first and third animations
        current_time = 1001000.0  # 1 second elapsed
        self.animation_manager.update_animations(current_time)
        
        # Only the 1.2 second animation should remain
        self.assertEqual(self.animation_manager.get_animation_count(), 1)
        remaining_animation = self.animation_manager.active_animations[0]
        self.assertEqual(remaining_animation["type"], self.SLIDE_DOWN)

    def test_update_animations_all_completed(self):
        """Test updating animations when all have completed."""
        # Add animations
        self.animation_manager.add_animation(self.FADE_IN, 500)
        self.animation_manager.add_animation(self.SLIDE_DOWN, 800)
        self.animation_manager.add_animation(self.BOUNCE, 300)
        
        # Update with time that completes all animations
        current_time = 1001000.0  # 1 second elapsed
        self.animation_manager.update_animations(current_time)
        
        # All animations should be removed
        self.assertEqual(self.animation_manager.get_animation_count(), 0)

    def test_update_animations_exact_completion_time(self):
        """Test updating animations at exact completion time."""
        self.animation_manager.add_animation(self.FADE_IN, 1000)  # Exactly 1 second
        
        # Update at exactly completion time
        current_time = 1001000.0  # Exactly 1 second elapsed
        self.animation_manager.update_animations(current_time)
        
        # Animation should be completed and removed
        self.assertEqual(self.animation_manager.get_animation_count(), 0)

    def test_update_animations_maintains_order(self):
        """Test that update_animations maintains order of remaining animations."""
        # Add animations in specific order
        self.animation_manager.add_animation("A", 2000)  # Long duration
        self.animation_manager.add_animation("B", 500)   # Short duration
        self.animation_manager.add_animation("C", 1500)  # Medium duration
        self.animation_manager.add_animation("D", 300)   # Very short duration
        
        # Update to complete B and D
        current_time = 1001000.0  # 1 second elapsed
        self.animation_manager.update_animations(current_time)
        
        # A and C should remain in their original relative order
        remaining = self.animation_manager.active_animations
        self.assertEqual(len(remaining), 2)
        self.assertEqual(remaining[0]["type"], "A")
        self.assertEqual(remaining[1]["type"], "C")

    def test_cleanup_animations_empty_list(self):
        """Test cleanup when no animations are active."""
        initial_count = self.animation_manager.get_animation_count()
        
        self.animation_manager.cleanup_animations()
        
        self.assertEqual(self.animation_manager.get_animation_count(), 0)

    def test_cleanup_animations_with_active_animations(self):
        """Test cleanup with active animations."""
        # Add several animations
        self.animation_manager.add_animation(self.FADE_IN, 1000)
        self.animation_manager.add_animation(self.SLIDE_DOWN, 500)
        self.animation_manager.add_animation(self.BOUNCE, 750)
        
        self.assertEqual(self.animation_manager.get_animation_count(), 3)
        
        self.animation_manager.cleanup_animations()
        
        # All animations should be removed
        self.assertEqual(self.animation_manager.get_animation_count(), 0)
        self.assertEqual(self.animation_manager.active_animations, [])

    def test_get_animation_count_consistency(self):
        """Test that get_animation_count is consistent with list length."""
        # Test with empty list
        self.assertEqual(self.animation_manager.get_animation_count(), 
                        len(self.animation_manager.active_animations))
        
        # Add animations and test consistency
        for i in range(5):
            self.animation_manager.add_animation(f"anim_{i}", 1000)
            self.assertEqual(self.animation_manager.get_animation_count(), 
                            len(self.animation_manager.active_animations))
        
        # Remove some and test consistency
        self.animation_manager.cleanup_animations()
        self.assertEqual(self.animation_manager.get_animation_count(), 
                        len(self.animation_manager.active_animations))

    def test_animation_data_structure(self):
        """Test that animation data structure contains expected fields."""
        target = Mock()
        self.animation_manager.add_animation(self.EXPLOSION, 250, target=target)
        
        animation = self.animation_manager.active_animations[0]
        
        # Verify all required fields exist
        self.assertIn("type", animation)
        self.assertIn("duration", animation)
        self.assertIn("start_time", animation)
        self.assertIn("target", animation)
        
        # Verify field values
        self.assertEqual(animation["type"], self.EXPLOSION)
        self.assertEqual(animation["duration"], 250)
        self.assertEqual(animation["start_time"], 1000000.0)
        self.assertEqual(animation["target"], target)

    def test_game_state_transitions(self):
        """Test complete game state transition cycle."""
        # Initial state
        self.assertEqual(self.animation_manager.game_state, "waiting")
        
        # Start game
        self.animation_manager.update(GAME_STARTED, {"time": 1000})
        self.assertEqual(self.animation_manager.game_state, "playing")
        
        # End game
        self.animation_manager.update(GAME_ENDED, {"time": 2000})
        self.assertEqual(self.animation_manager.game_state, "ended")

    def test_integration_game_event_flow(self):
        """Test realistic game event flow with animations."""
        # Game starts
        self.animation_manager.update(GAME_STARTED, {"time": 0, "players": ["Alice", "Bob"]})
        self.assertEqual(self.animation_manager.game_state, "playing")
        
        # Add some gameplay animations
        piece1 = Mock()
        piece1.piece_id = "KW1"
        piece2 = Mock()
        piece2.piece_id = "QB1"
        
        self.animation_manager.add_animation("piece_move", 800, target=piece1)
        self.animation_manager.add_animation("piece_capture", 300, target=piece2)
        self.animation_manager.add_animation("board_highlight", 200)
        
        self.assertEqual(self.animation_manager.get_animation_count(), 3)
        
        # Some time passes, update animations
        self.animation_manager.update_animations(1000400.0)  # 400ms elapsed
        
        # Short animations should be complete
        self.assertEqual(self.animation_manager.get_animation_count(), 1)  # Only piece_move remains
        
        # Game ends - should cleanup remaining animations
        self.animation_manager.update(GAME_ENDED, {"time": 5000, "winner": "Alice"})
        
        self.assertEqual(self.animation_manager.game_state, "ended")
        self.assertEqual(self.animation_manager.get_animation_count(), 0)

    def test_multiple_game_cycles(self):
        """Test multiple game start/end cycles."""
        for cycle in range(3):
            # Start game
            self.animation_manager.update(GAME_STARTED, {"time": cycle * 1000})
            self.assertEqual(self.animation_manager.game_state, "playing")
            
            # Add animations
            self.animation_manager.add_animation(f"cycle_{cycle}", 500)
            self.assertEqual(self.animation_manager.get_animation_count(), 1)
            
            # End game
            self.animation_manager.update(GAME_ENDED, {"time": (cycle + 1) * 1000})
            self.assertEqual(self.animation_manager.game_state, "ended")
            self.assertEqual(self.animation_manager.get_animation_count(), 0)

    def test_time_precision(self):
        """Test time handling precision with floating point values."""
        # Test with floating point durations
        self.animation_manager.add_animation(self.FADE_IN, 1000.5)
        
        animation = self.animation_manager.active_animations[0]
        self.assertEqual(animation["duration"], 1000.5)
        
        # Test update with floating point time
        current_time = 1001000.6  # 1000.6ms elapsed
        self.animation_manager.update_animations(current_time)
        
        # Animation should be completed (1000.6 > 1000.5)
        self.assertEqual(self.animation_manager.get_animation_count(), 0)

    def test_animation_timing_edge_cases(self):
        """Test edge cases in animation timing."""
        # Test immediate completion (0 duration)
        self.animation_manager.add_animation(self.FADE_IN, 0)
        self.animation_manager.update_animations(1000000.1)  # Any time after start
        self.assertEqual(self.animation_manager.get_animation_count(), 0)
        
        # Test negative duration behavior
        self.animation_manager.add_animation(self.SLIDE_DOWN, -100)
        self.animation_manager.update_animations(1000000.0)  # Same time as start
        self.assertEqual(self.animation_manager.get_animation_count(), 0)


if __name__ == '__main__':
    unittest.main()
