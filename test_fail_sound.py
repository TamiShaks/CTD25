#!/usr/bin/env python3
"""
🧪 Test Invalid Move Sound
=========================

Quick test to verify that invalid move sound plays correctly.
"""

import pygame
import time
from It1_interfaces.EventBus import EventBus
from It1_interfaces.SoundManager import SoundManager
from It1_interfaces.EventTypes import INVALID_MOVE

def test_invalid_move_sound():
    """Test that invalid move sound plays correctly"""
    print("🔊 Testing Invalid Move Sound...")
    
    # Initialize EventBus and SoundManager
    event_bus = EventBus()
    sound_manager = SoundManager()
    
    # Subscribe sound manager to invalid move events
    event_bus.subscribe(INVALID_MOVE, sound_manager)
    
    # Test data for invalid move
    invalid_move_data = {
        "player": "A",
        "piece_id": "PW1",
        "from_pos": (6, 0),
        "to_pos": (4, 0),
        "reason": "Invalid chess rule"
    }
    
    print("🎵 Playing fail sound...")
    
    # Publish invalid move event - should trigger fail.mp3
    event_bus.publish(INVALID_MOVE, invalid_move_data)
    
    # Wait a bit for sound to play
    time.sleep(2)
    
    print("✅ Test completed! You should have heard the fail sound.")
    
    # Clean up pygame
    pygame.mixer.quit()

if __name__ == "__main__":
    test_invalid_move_sound()
