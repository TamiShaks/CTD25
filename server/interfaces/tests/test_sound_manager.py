"""
Comprehensive test suite for SoundManager class.

Tests the sound system including:
- Sound manager initialization and setup
- Event-based sound playing
- Sound file existence checking
- Error handling and fallback behavior
- Custom sound playing
- Pygame mixer integration
- Sound enabling/disabling functionality
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
import sys
import os

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Add main project directory for imports
main_dir = os.path.dirname(parent_dir)
sys.path.insert(0, main_dir)

from SoundManager import SoundManager
from EventTypes import MOVE_DONE, PIECE_CAPTURED, GAME_ENDED, GAME_STARTED


class TestSoundManager(unittest.TestCase):
    """Test suite for SoundManager class covering all sound functionality."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock pygame to avoid actual sound initialization
        self.pygame_patcher = patch('It1_interfaces.SoundManager.pygame')
        self.mock_pygame = self.pygame_patcher.start()
        
        # Mock os.path.exists to control which sound files "exist"
        self.exists_patcher = patch('It1_interfaces.SoundManager.os.path.exists')
        self.mock_exists = self.exists_patcher.start()
        
        # By default, assume all sound files exist
        self.mock_exists.return_value = True
        
        # Mock pygame.mixer components
        self.mock_pygame.mixer.init.return_value = None
        self.mock_pygame.mixer.music = Mock()
        
        # Create SoundManager instance
        self.sound_manager = SoundManager()

    def tearDown(self):
        """Clean up after each test method."""
        self.pygame_patcher.stop()
        self.exists_patcher.stop()

    def test_sound_manager_initialization_success(self):
        """Test successful SoundManager initialization."""
        manager = SoundManager()
        
        self.assertIsInstance(manager, SoundManager)
        self.assertTrue(manager.sounds_enabled)
        
        # Verify pygame mixer was initialized
        self.mock_pygame.mixer.init.assert_called()
        
        # Verify sound mappings exist
        expected_sounds = {
            MOVE_DONE: "sounds/5movement0.wav",
            PIECE_CAPTURED: "sounds/gan.wav",
            GAME_ENDED: "sounds/applause.mp3",
            GAME_STARTED: "sounds/1TADA.WAV"
        }
        self.assertEqual(manager.sounds, expected_sounds)
        
        # Since all files "exist", available_sounds should match
        self.assertEqual(manager.available_sounds, expected_sounds)

    def test_sound_manager_initialization_pygame_failure(self):
        """Test SoundManager initialization when pygame fails."""
        # Make pygame.mixer.init raise an exception
        self.mock_pygame.mixer.init.side_effect = Exception("Pygame init failed")
        
        manager = SoundManager()
        
        self.assertFalse(manager.sounds_enabled)
        self.assertEqual(manager.available_sounds, {})

    def test_sound_manager_initialization_partial_sound_files(self):
        """Test initialization when only some sound files exist."""
        # Only MOVE_DONE and GAME_STARTED files exist
        def mock_exists_side_effect(path):
            return path in ["sounds/5movement0.wav", "sounds/1TADA.WAV"]
        
        self.mock_exists.side_effect = mock_exists_side_effect
        
        manager = SoundManager()
        
        self.assertTrue(manager.sounds_enabled)
        expected_available = {
            MOVE_DONE: "sounds/5movement0.wav",
            GAME_STARTED: "sounds/1TADA.WAV"
        }
        self.assertEqual(manager.available_sounds, expected_available)

    def test_sound_manager_initialization_no_sound_files(self):
        """Test initialization when no sound files exist."""
        self.mock_exists.return_value = False
        
        manager = SoundManager()
        
        self.assertTrue(manager.sounds_enabled)  # pygame worked, but no files
        self.assertEqual(manager.available_sounds, {})

    def test_update_move_done_event(self):
        """Test playing sound for MOVE_DONE event."""
        test_data = {"piece_id": "PW1", "move": {"from": (6, 0), "to": (5, 0)}}
        
        self.sound_manager.update(MOVE_DONE, test_data)
        
        # Verify sound was played
        self.mock_pygame.mixer.music.stop.assert_called_once()
        self.mock_pygame.mixer.music.load.assert_called_once_with("sounds/5movement0.wav")
        self.mock_pygame.mixer.music.play.assert_called_once()

    def test_update_piece_captured_event(self):
        """Test playing sound for PIECE_CAPTURED event."""
        test_data = {"captured_piece": "QB1", "by_player": "Alice"}
        
        self.sound_manager.update(PIECE_CAPTURED, test_data)
        
        # Verify sound was played
        self.mock_pygame.mixer.music.stop.assert_called_once()
        self.mock_pygame.mixer.music.load.assert_called_once_with("sounds/gan.wav")
        self.mock_pygame.mixer.music.play.assert_called_once()

    def test_update_game_started_event(self):
        """Test playing sound for GAME_STARTED event."""
        test_data = {"players": ["Alice", "Bob"], "timestamp": 12345}
        
        self.sound_manager.update(GAME_STARTED, test_data)
        
        # Verify sound was played
        self.mock_pygame.mixer.music.stop.assert_called_once()
        self.mock_pygame.mixer.music.load.assert_called_once_with("sounds/1TADA.WAV")
        self.mock_pygame.mixer.music.play.assert_called_once()

    def test_update_game_ended_event(self):
        """Test playing sound for GAME_ENDED event."""
        test_data = {"winner": "Bob", "game_time": 300}
        
        self.sound_manager.update(GAME_ENDED, test_data)
        
        # Verify sound was played
        self.mock_pygame.mixer.music.stop.assert_called_once()
        self.mock_pygame.mixer.music.load.assert_called_once_with("sounds/applause.mp3")
        self.mock_pygame.mixer.music.play.assert_called_once()

    def test_update_unknown_event(self):
        """Test handling unknown event types."""
        self.sound_manager.update("UNKNOWN_EVENT", {"data": "test"})
        
        # No sound operations should be performed
        self.mock_pygame.mixer.music.stop.assert_not_called()
        self.mock_pygame.mixer.music.load.assert_not_called()
        self.mock_pygame.mixer.music.play.assert_not_called()

    def test_update_sounds_disabled(self):
        """Test update when sounds are disabled."""
        self.sound_manager.sounds_enabled = False
        
        self.sound_manager.update(MOVE_DONE, {"test": "data"})
        
        # No sound operations should be performed
        self.mock_pygame.mixer.music.stop.assert_not_called()
        self.mock_pygame.mixer.music.load.assert_not_called()
        self.mock_pygame.mixer.music.play.assert_not_called()

    def test_update_sound_file_not_available(self):
        """Test update when sound file is not available."""
        # Remove MOVE_DONE from available sounds
        self.sound_manager.available_sounds = {
            PIECE_CAPTURED: "sounds/gan.wav",
            GAME_ENDED: "sounds/applause.mp3",
            GAME_STARTED: "sounds/1TADA.WAV"
        }
        
        self.sound_manager.update(MOVE_DONE, {"test": "data"})
        
        # No sound operations should be performed
        self.mock_pygame.mixer.music.stop.assert_not_called()
        self.mock_pygame.mixer.music.load.assert_not_called()
        self.mock_pygame.mixer.music.play.assert_not_called()

    def test_update_pygame_exception_during_playback(self):
        """Test handling pygame exceptions during sound playback."""
        # Make pygame operations raise exceptions
        self.mock_pygame.mixer.music.load.side_effect = Exception("Sound loading failed")
        
        # Should not raise exception
        self.sound_manager.update(MOVE_DONE, {"test": "data"})
        
        # Stop should still be called, but load would fail
        self.mock_pygame.mixer.music.stop.assert_called_once()
        self.mock_pygame.mixer.music.load.assert_called_once_with("sounds/5movement0.wav")

    def test_update_with_none_data(self):
        """Test update with None data."""
        # Should not raise exception
        self.sound_manager.update(MOVE_DONE, None)
        
        # Sound should still play since data is not used for sound selection
        self.mock_pygame.mixer.music.stop.assert_called_once()
        self.mock_pygame.mixer.music.load.assert_called_once_with("sounds/5movement0.wav")
        self.mock_pygame.mixer.music.play.assert_called_once()

    def test_play_custom_sound_success(self):
        """Test playing custom sound file successfully."""
        custom_sound = "sounds/custom_sound.wav"
        
        result = self.sound_manager.play_custom_sound(custom_sound)
        
        self.assertTrue(result)
        self.mock_pygame.mixer.music.stop.assert_called_once()
        self.mock_pygame.mixer.music.load.assert_called_once_with(custom_sound)
        self.mock_pygame.mixer.music.play.assert_called_once()

    def test_play_custom_sound_file_not_exists(self):
        """Test playing custom sound when file doesn't exist."""
        custom_sound = "sounds/nonexistent.wav"
        self.mock_exists.return_value = False
        
        result = self.sound_manager.play_custom_sound(custom_sound)
        
        self.assertFalse(result)
        # No pygame operations should be performed
        self.mock_pygame.mixer.music.stop.assert_not_called()
        self.mock_pygame.mixer.music.load.assert_not_called()
        self.mock_pygame.mixer.music.play.assert_not_called()

    def test_play_custom_sound_sounds_disabled(self):
        """Test playing custom sound when sounds are disabled."""
        self.sound_manager.sounds_enabled = False
        custom_sound = "sounds/custom_sound.wav"
        
        result = self.sound_manager.play_custom_sound(custom_sound)
        
        self.assertFalse(result)
        # No pygame operations should be performed
        self.mock_pygame.mixer.music.stop.assert_not_called()

    def test_play_custom_sound_pygame_exception(self):
        """Test playing custom sound when pygame raises exception."""
        self.mock_pygame.mixer.music.play.side_effect = Exception("Playback failed")
        custom_sound = "sounds/custom_sound.wav"
        
        result = self.sound_manager.play_custom_sound(custom_sound)
        
        self.assertFalse(result)
        # Operations should be attempted but return False due to exception
        self.mock_pygame.mixer.music.stop.assert_called_once()
        self.mock_pygame.mixer.music.load.assert_called_once_with(custom_sound)
        self.mock_pygame.mixer.music.play.assert_called_once()

    def test_multiple_sound_events_sequence(self):
        """Test sequence of multiple sound events."""
        # Sequence of game events
        events = [
            (GAME_STARTED, {"players": ["Alice", "Bob"]}),
            (MOVE_DONE, {"piece_id": "PW1"}),
            (MOVE_DONE, {"piece_id": "PB1"}),
            (PIECE_CAPTURED, {"piece": "PW1"}),
            (MOVE_DONE, {"piece_id": "QB1"}),
            (GAME_ENDED, {"winner": "Bob"})
        ]
        
        for event_type, data in events:
            self.sound_manager.update(event_type, data)
        
        # Verify each sound was played (stop should be called for each)
        self.assertEqual(self.mock_pygame.mixer.music.stop.call_count, 6)
        self.assertEqual(self.mock_pygame.mixer.music.load.call_count, 6)
        self.assertEqual(self.mock_pygame.mixer.music.play.call_count, 6)
        
        # Verify correct sound files were loaded
        expected_calls = [
            call("sounds/1TADA.WAV"),    # GAME_STARTED
            call("sounds/5movement0.wav"), # MOVE_DONE
            call("sounds/5movement0.wav"), # MOVE_DONE
            call("sounds/gan.wav"),       # PIECE_CAPTURED
            call("sounds/5movement0.wav"), # MOVE_DONE
            call("sounds/applause.mp3")   # GAME_ENDED
        ]
        self.mock_pygame.mixer.music.load.assert_has_calls(expected_calls)

    def test_sound_file_path_variations(self):
        """Test different sound file path formats."""
        # Test with different file extensions and paths
        test_files = [
            "sounds/test.wav",
            "sounds/test.mp3",
            "sounds/subfolder/test.ogg",
            "/absolute/path/test.wav",
            "relative/path/test.mp3"
        ]
        
        for sound_file in test_files:
            # Reset mocks
            self.mock_pygame.mixer.music.reset_mock()
            
            result = self.sound_manager.play_custom_sound(sound_file)
            
            self.assertTrue(result)
            self.mock_pygame.mixer.music.load.assert_called_once_with(sound_file)

    def test_concurrent_sound_playing(self):
        """Test that new sounds stop previous ones."""
        # Play first sound
        self.sound_manager.update(MOVE_DONE, {})
        
        # Verify first sound operations
        self.assertEqual(self.mock_pygame.mixer.music.stop.call_count, 1)
        self.assertEqual(self.mock_pygame.mixer.music.load.call_count, 1)
        self.assertEqual(self.mock_pygame.mixer.music.play.call_count, 1)
        
        # Play second sound
        self.sound_manager.update(PIECE_CAPTURED, {})
        
        # Verify stop was called again (stopping previous sound)
        self.assertEqual(self.mock_pygame.mixer.music.stop.call_count, 2)
        self.assertEqual(self.mock_pygame.mixer.music.load.call_count, 2)
        self.assertEqual(self.mock_pygame.mixer.music.play.call_count, 2)

    def test_sound_mapping_completeness(self):
        """Test that all event types have sound mappings."""
        manager = SoundManager()
        
        # All important event types should have sound mappings
        expected_events = [MOVE_DONE, PIECE_CAPTURED, GAME_STARTED, GAME_ENDED]
        
        for event_type in expected_events:
            self.assertIn(event_type, manager.sounds)
            self.assertIsInstance(manager.sounds[event_type], str)
            self.assertTrue(manager.sounds[event_type].startswith("sounds/"))

    def test_sound_manager_state_consistency(self):
        """Test that SoundManager maintains consistent state."""
        manager = SoundManager()
        
        # Initially enabled with available sounds
        self.assertTrue(manager.sounds_enabled)
        self.assertIsInstance(manager.available_sounds, dict)
        
        # Disable sounds manually
        manager.sounds_enabled = False
        
        # Update should not perform any operations
        manager.update(MOVE_DONE, {})
        
        # No sound operations should have been performed
        self.mock_pygame.mixer.music.stop.assert_not_called()

    def test_integration_realistic_game_flow(self):
        """Test realistic game flow with sound events."""
        # Simulate a complete game with sounds
        game_events = [
            # Game starts
            (GAME_STARTED, {"players": ["Alice", "Bob"], "timestamp": 0}),
            
            # Several moves
            (MOVE_DONE, {"piece_id": "PW1", "from": (6, 0), "to": (5, 0)}),
            (MOVE_DONE, {"piece_id": "PB1", "from": (1, 0), "to": (2, 0)}),
            (MOVE_DONE, {"piece_id": "NW1", "from": (7, 1), "to": (5, 2)}),
            
            # Capture occurs
            (PIECE_CAPTURED, {"piece": "PB1", "by": "NW1"}),
            
            # More moves
            (MOVE_DONE, {"piece_id": "QB1", "from": (0, 3), "to": (4, 7)}),
            (MOVE_DONE, {"piece_id": "KW1", "from": (7, 4), "to": (6, 4)}),
            
            # Game ends
            (GAME_ENDED, {"winner": "Alice", "reason": "checkmate"})
        ]
        
        for event_type, data in game_events:
            self.sound_manager.update(event_type, data)
        
        # Verify all events triggered sounds
        total_events = len(game_events)
        self.assertEqual(self.mock_pygame.mixer.music.stop.call_count, total_events)
        self.assertEqual(self.mock_pygame.mixer.music.load.call_count, total_events)
        self.assertEqual(self.mock_pygame.mixer.music.play.call_count, total_events)
        
        # Verify variety of sounds were played
        load_calls = [call.args[0] for call in self.mock_pygame.mixer.music.load.call_args_list]
        
        # Should contain different sound files
        self.assertIn("sounds/1TADA.WAV", load_calls)      # Game start
        self.assertIn("sounds/5movement0.wav", load_calls)  # Moves
        self.assertIn("sounds/gan.wav", load_calls)         # Capture
        self.assertIn("sounds/applause.mp3", load_calls)    # Game end

    def test_error_recovery(self):
        """Test that SoundManager recovers gracefully from errors."""
        # Make one sound operation fail
        self.mock_pygame.mixer.music.load.side_effect = [
            Exception("First load fails"),
            None,  # Second load succeeds
            None   # Third load succeeds
        ]
        
        # Try to play sounds despite errors
        self.sound_manager.update(MOVE_DONE, {})      # Should fail silently
        self.sound_manager.update(PIECE_CAPTURED, {}) # Should succeed
        self.sound_manager.update(GAME_ENDED, {})     # Should succeed
        
        # All stop operations should have been attempted
        self.assertEqual(self.mock_pygame.mixer.music.stop.call_count, 3)
        
        # All load operations should have been attempted
        self.assertEqual(self.mock_pygame.mixer.music.load.call_count, 3)


if __name__ == '__main__':
    unittest.main()
