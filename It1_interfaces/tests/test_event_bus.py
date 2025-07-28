"""
Comprehensive test suite for EventBus class.

Tests the event system including:
- Event subscription and unsubscription
- Event publishing and notification
- Multiple subscribers handling
- Data passing with events
- Edge cases and error handling
- Cleanup and memory management
"""

import unittest
from unittest.mock import Mock, MagicMock, call
import sys
import os

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from EventBus import EventBus


class TestEventBus(unittest.TestCase):
    """Test suite for EventBus class covering all event functionality."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.event_bus = EventBus()
        
        # Create mock subscribers
        self.subscriber1 = Mock()
        self.subscriber2 = Mock()
        self.subscriber3 = Mock()
        
        # Define test event types
        self.GAME_START = "GAME_START"
        self.PLAYER_MOVE = "PLAYER_MOVE"
        self.PIECE_CAPTURED = "PIECE_CAPTURED"
        self.GAME_END = "GAME_END"

    def test_eventbus_initialization(self):
        """Test EventBus initialization."""
        event_bus = EventBus()
        
        self.assertIsInstance(event_bus, EventBus)
        self.assertEqual(event_bus.subscribers, {})
        self.assertIsInstance(event_bus.subscribers, dict)

    def test_subscribe_single_subscriber(self):
        """Test subscribing a single subscriber to an event."""
        self.event_bus.subscribe(self.GAME_START, self.subscriber1)
        
        # Verify subscriber was added
        self.assertIn(self.GAME_START, self.event_bus.subscribers)
        self.assertIn(self.subscriber1, self.event_bus.subscribers[self.GAME_START])
        self.assertEqual(len(self.event_bus.subscribers[self.GAME_START]), 1)

    def test_subscribe_multiple_subscribers_same_event(self):
        """Test subscribing multiple subscribers to the same event."""
        self.event_bus.subscribe(self.GAME_START, self.subscriber1)
        self.event_bus.subscribe(self.GAME_START, self.subscriber2)
        self.event_bus.subscribe(self.GAME_START, self.subscriber3)
        
        # Verify all subscribers were added
        self.assertIn(self.GAME_START, self.event_bus.subscribers)
        subscribers = self.event_bus.subscribers[self.GAME_START]
        
        self.assertIn(self.subscriber1, subscribers)
        self.assertIn(self.subscriber2, subscribers)
        self.assertIn(self.subscriber3, subscribers)
        self.assertEqual(len(subscribers), 3)

    def test_subscribe_multiple_events_same_subscriber(self):
        """Test subscribing the same subscriber to multiple events."""
        self.event_bus.subscribe(self.GAME_START, self.subscriber1)
        self.event_bus.subscribe(self.PLAYER_MOVE, self.subscriber1)
        self.event_bus.subscribe(self.GAME_END, self.subscriber1)
        
        # Verify subscriber is in all event lists
        self.assertIn(self.subscriber1, self.event_bus.subscribers[self.GAME_START])
        self.assertIn(self.subscriber1, self.event_bus.subscribers[self.PLAYER_MOVE])
        self.assertIn(self.subscriber1, self.event_bus.subscribers[self.GAME_END])
        
        # Verify separate event lists
        self.assertEqual(len(self.event_bus.subscribers), 3)

    def test_subscribe_same_subscriber_twice_same_event(self):
        """Test subscribing the same subscriber twice to the same event."""
        self.event_bus.subscribe(self.GAME_START, self.subscriber1)
        self.event_bus.subscribe(self.GAME_START, self.subscriber1)
        
        # Should have two entries (EventBus allows duplicates)
        subscribers = self.event_bus.subscribers[self.GAME_START]
        self.assertEqual(len(subscribers), 2)
        self.assertEqual(subscribers.count(self.subscriber1), 2)

    def test_publish_single_subscriber(self):
        """Test publishing event to single subscriber."""
        self.event_bus.subscribe(self.GAME_START, self.subscriber1)
        
        test_data = {"game_id": 123, "players": ["Alice", "Bob"]}
        self.event_bus.publish(self.GAME_START, test_data)
        
        # Verify subscriber was called with correct parameters
        self.subscriber1.update.assert_called_once_with(self.GAME_START, test_data)

    def test_publish_multiple_subscribers(self):
        """Test publishing event to multiple subscribers."""
        self.event_bus.subscribe(self.GAME_START, self.subscriber1)
        self.event_bus.subscribe(self.GAME_START, self.subscriber2)
        self.event_bus.subscribe(self.GAME_START, self.subscriber3)
        
        test_data = {"timestamp": 12345}
        self.event_bus.publish(self.GAME_START, test_data)
        
        # Verify all subscribers were called
        self.subscriber1.update.assert_called_once_with(self.GAME_START, test_data)
        self.subscriber2.update.assert_called_once_with(self.GAME_START, test_data)
        self.subscriber3.update.assert_called_once_with(self.GAME_START, test_data)

    def test_publish_no_data(self):
        """Test publishing event without data."""
        self.event_bus.subscribe(self.GAME_START, self.subscriber1)
        
        self.event_bus.publish(self.GAME_START)
        
        # Should be called with None data
        self.subscriber1.update.assert_called_once_with(self.GAME_START, None)

    def test_publish_with_explicit_none_data(self):
        """Test publishing event with explicitly None data."""
        self.event_bus.subscribe(self.GAME_START, self.subscriber1)
        
        self.event_bus.publish(self.GAME_START, None)
        
        self.subscriber1.update.assert_called_once_with(self.GAME_START, None)

    def test_publish_nonexistent_event(self):
        """Test publishing to event type with no subscribers."""
        # This should not raise an exception
        self.event_bus.publish("NONEXISTENT_EVENT", {"data": "test"})
        
        # No subscribers should be called
        self.subscriber1.update.assert_not_called()

    def test_publish_with_complex_data(self):
        """Test publishing event with complex data structures."""
        self.event_bus.subscribe(self.PLAYER_MOVE, self.subscriber1)
        
        complex_data = {
            "player": "Alice",
            "piece": {"type": "pawn", "color": "white"},
            "move": {"from": (6, 0), "to": (5, 0)},
            "timestamp": 12345,
            "metadata": {
                "valid": True,
                "captures": [],
                "special_moves": None
            }
        }
        
        self.event_bus.publish(self.PLAYER_MOVE, complex_data)
        
        self.subscriber1.update.assert_called_once_with(self.PLAYER_MOVE, complex_data)

    def test_unsubscribe_existing_subscriber(self):
        """Test unsubscribing an existing subscriber."""
        self.event_bus.subscribe(self.GAME_START, self.subscriber1)
        self.event_bus.subscribe(self.GAME_START, self.subscriber2)
        
        # Unsubscribe one subscriber
        self.event_bus.unsubscribe(self.GAME_START, self.subscriber1)
        
        # Verify subscriber was removed
        subscribers = self.event_bus.subscribers[self.GAME_START]
        self.assertNotIn(self.subscriber1, subscribers)
        self.assertIn(self.subscriber2, subscribers)
        self.assertEqual(len(subscribers), 1)

    def test_unsubscribe_last_subscriber_removes_event(self):
        """Test that unsubscribing the last subscriber removes the event type."""
        self.event_bus.subscribe(self.GAME_START, self.subscriber1)
        
        # Unsubscribe the only subscriber
        self.event_bus.unsubscribe(self.GAME_START, self.subscriber1)
        
        # Event type should be completely removed
        self.assertNotIn(self.GAME_START, self.event_bus.subscribers)

    def test_unsubscribe_nonexistent_subscriber(self):
        """Test unsubscribing a subscriber that was never subscribed."""
        self.event_bus.subscribe(self.GAME_START, self.subscriber1)
        
        # This should raise ValueError when trying to remove non-existent item
        with self.assertRaises(ValueError):
            self.event_bus.unsubscribe(self.GAME_START, self.subscriber2)

    def test_unsubscribe_from_nonexistent_event(self):
        """Test unsubscribing from an event type that doesn't exist."""
        # This should not raise an exception
        self.event_bus.unsubscribe("NONEXISTENT_EVENT", self.subscriber1)
        
        # Subscribers dict should remain empty
        self.assertEqual(self.event_bus.subscribers, {})

    def test_unsubscribe_duplicate_subscriber(self):
        """Test unsubscribing when subscriber is subscribed multiple times."""
        self.event_bus.subscribe(self.GAME_START, self.subscriber1)
        self.event_bus.subscribe(self.GAME_START, self.subscriber1)  # Subscribe twice
        
        # Unsubscribe once
        self.event_bus.unsubscribe(self.GAME_START, self.subscriber1)
        
        # Should still have one instance of the subscriber
        subscribers = self.event_bus.subscribers[self.GAME_START]
        self.assertIn(self.subscriber1, subscribers)
        self.assertEqual(len(subscribers), 1)

    def test_publish_after_unsubscribe(self):
        """Test that unsubscribed subscribers don't receive events."""
        self.event_bus.subscribe(self.GAME_START, self.subscriber1)
        self.event_bus.subscribe(self.GAME_START, self.subscriber2)
        
        # Unsubscribe one subscriber
        self.event_bus.unsubscribe(self.GAME_START, self.subscriber1)
        
        # Publish event
        self.event_bus.publish(self.GAME_START, {"test": "data"})
        
        # Only remaining subscriber should be called
        self.subscriber1.update.assert_not_called()
        self.subscriber2.update.assert_called_once_with(self.GAME_START, {"test": "data"})

    def test_subscriber_update_method_called_correctly(self):
        """Test that subscriber's update method is called with correct signature."""
        self.event_bus.subscribe(self.PLAYER_MOVE, self.subscriber1)
        
        event_data = {"player": "test", "move": "data"}
        self.event_bus.publish(self.PLAYER_MOVE, event_data)
        
        # Verify the exact call signature
        expected_call = call(self.PLAYER_MOVE, event_data)
        self.subscriber1.update.assert_has_calls([expected_call])

    def test_multiple_events_independence(self):
        """Test that different event types are handled independently."""
        # Subscribe to different events
        self.event_bus.subscribe(self.GAME_START, self.subscriber1)
        self.event_bus.subscribe(self.PLAYER_MOVE, self.subscriber2)
        self.event_bus.subscribe(self.GAME_END, self.subscriber3)
        
        # Publish to one event type
        self.event_bus.publish(self.PLAYER_MOVE, {"test": "move"})
        
        # Only the subscriber for that event should be called
        self.subscriber1.update.assert_not_called()
        self.subscriber2.update.assert_called_once_with(self.PLAYER_MOVE, {"test": "move"})
        self.subscriber3.update.assert_not_called()

    def test_eventbus_state_consistency(self):
        """Test that EventBus maintains consistent state through operations."""
        # Start with empty state
        self.assertEqual(len(self.event_bus.subscribers), 0)
        
        # Add subscribers
        self.event_bus.subscribe(self.GAME_START, self.subscriber1)
        self.assertEqual(len(self.event_bus.subscribers), 1)
        
        self.event_bus.subscribe(self.PLAYER_MOVE, self.subscriber2)
        self.assertEqual(len(self.event_bus.subscribers), 2)
        
        # Remove subscribers
        self.event_bus.unsubscribe(self.GAME_START, self.subscriber1)
        self.assertEqual(len(self.event_bus.subscribers), 1)
        
        self.event_bus.unsubscribe(self.PLAYER_MOVE, self.subscriber2)
        self.assertEqual(len(self.event_bus.subscribers), 0)

    def test_subscriber_exception_handling(self):
        """Test behavior when subscriber's update method raises an exception."""
        # Create a subscriber that raises an exception
        failing_subscriber = Mock()
        failing_subscriber.update.side_effect = Exception("Subscriber error")
        
        working_subscriber = Mock()
        
        self.event_bus.subscribe(self.GAME_START, failing_subscriber)
        self.event_bus.subscribe(self.GAME_START, working_subscriber)
        
        # Publishing should propagate the exception
        with self.assertRaises(Exception):
            self.event_bus.publish(self.GAME_START, {"test": "data"})
        
        # The failing subscriber should have been called
        failing_subscriber.update.assert_called_once()

    def test_integration_game_events_flow(self):
        """Test realistic game event flow integration."""
        # Create specialized mock subscribers
        game_manager = Mock()
        ui_manager = Mock()
        sound_manager = Mock()
        statistics_manager = Mock()
        
        # Subscribe to relevant events
        self.event_bus.subscribe(self.GAME_START, game_manager)
        self.event_bus.subscribe(self.GAME_START, ui_manager)
        self.event_bus.subscribe(self.GAME_START, sound_manager)
        
        self.event_bus.subscribe(self.PLAYER_MOVE, game_manager)
        self.event_bus.subscribe(self.PLAYER_MOVE, statistics_manager)
        
        self.event_bus.subscribe(self.PIECE_CAPTURED, ui_manager)
        self.event_bus.subscribe(self.PIECE_CAPTURED, sound_manager)
        
        self.event_bus.subscribe(self.GAME_END, game_manager)
        self.event_bus.subscribe(self.GAME_END, ui_manager)
        self.event_bus.subscribe(self.GAME_END, statistics_manager)
        
        # Simulate game flow
        # 1. Game starts
        self.event_bus.publish(self.GAME_START, {"players": ["Alice", "Bob"]})
        
        # 2. Player makes move
        self.event_bus.publish(self.PLAYER_MOVE, {
            "player": "Alice",
            "from": (6, 0),
            "to": (5, 0)
        })
        
        # 3. Piece is captured
        self.event_bus.publish(self.PIECE_CAPTURED, {
            "captured_piece": "pawn",
            "by_player": "Bob"
        })
        
        # 4. Game ends
        self.event_bus.publish(self.GAME_END, {"winner": "Bob"})
        
        # Verify all managers received appropriate events
        self.assertEqual(game_manager.update.call_count, 3)  # GAME_START, PLAYER_MOVE, GAME_END
        self.assertEqual(ui_manager.update.call_count, 3)    # GAME_START, PIECE_CAPTURED, GAME_END
        self.assertEqual(sound_manager.update.call_count, 2) # GAME_START, PIECE_CAPTURED
        self.assertEqual(statistics_manager.update.call_count, 2) # PLAYER_MOVE, GAME_END


if __name__ == '__main__':
    unittest.main()
