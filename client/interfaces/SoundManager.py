import pygame
import os
from typing import Dict, Optional
from EventTypes import MOVE_DONE, PIECE_CAPTURED, GAME_ENDED, GAME_STARTED, INVALID_MOVE


class SoundManager:
    """Manages game sounds and audio playback."""
    
    # Sound configuration constants
    DEFAULT_SOUNDS = {
        MOVE_DONE: "client/sounds/5movement0.wav",
        PIECE_CAPTURED: "client/sounds/gan.wav",
        GAME_ENDED: "client/sounds/applause.mp3",
        GAME_STARTED: "client/sounds/1TADA.WAV",
        INVALID_MOVE: "client/sounds/fail.mp3"
    }
    
    def __init__(self, volume: float = 0.5):
        """Initialize the sound manager with optional volume control."""
        self.volume = max(0.0, min(1.0, volume))  # Clamp volume between 0-1
        self.sounds_enabled = self._initialize_mixer()
        self.available_sounds = self._load_available_sounds() if self.sounds_enabled else {}
        self.loaded_sounds = {}  # Cache for loaded sounds

    def _initialize_mixer(self) -> bool:
        """Initialize pygame mixer and return success status."""
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.music.set_volume(self.volume)
            return True
        except Exception as e:
            print(f"Failed to initialize sound mixer: {e}")
            return False

    def _load_available_sounds(self) -> Dict[str, str]:
        """Load and validate available sound files."""
        available = {}
        for event_type, sound_file in self.DEFAULT_SOUNDS.items():
            if self._is_sound_file_valid(sound_file):
                available[event_type] = sound_file
            else:
                print(f"Warning: Sound file not found: {sound_file}")
        
        print(f"Loaded {len(available)}/{len(self.DEFAULT_SOUNDS)} sound files")
        return available

    def _is_sound_file_valid(self, sound_file: str) -> bool:
        """Check if a sound file exists and is accessible."""
        return os.path.exists(sound_file) and os.path.isfile(sound_file)

    def _play_sound_file(self, sound_file: str) -> bool:
        """Core method to play a sound file."""
        if not self.sounds_enabled:
            return False
            
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play()
            return True
        except Exception as e:
            print(f"Error playing sound {sound_file}: {e}")
            return False

    def update(self, event_type, data):
        """Handle sound events from the game."""
        if not self.sounds_enabled:
            return
            
        sound_file = self.available_sounds.get(event_type)
        if sound_file:
            self._play_sound_file(sound_file)

    def play_custom_sound(self, sound_file: str) -> bool:
        """Play a custom sound file."""
        if not self.sounds_enabled:
            return False
            
        if self._is_sound_file_valid(sound_file):
            return self._play_sound_file(sound_file)
        else:
            print(f"Custom sound file not found: {sound_file}")
            return False

    def set_volume(self, volume: float):
        """Set the volume for sound playback (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        if self.sounds_enabled:
            pygame.mixer.music.set_volume(self.volume)

    def toggle_sounds(self) -> bool:
        """Toggle sound on/off and return new state."""
        if self.sounds_enabled:
            pygame.mixer.music.stop()
        self.sounds_enabled = not self.sounds_enabled
        return self.sounds_enabled

    def stop_all_sounds(self):
        """Stop all currently playing sounds."""
        if self.sounds_enabled:
            pygame.mixer.music.stop()

    def is_playing(self) -> bool:
        """Check if any sound is currently playing."""
        if not self.sounds_enabled:
            return False
        return pygame.mixer.music.get_busy()

    def get_status(self) -> Dict[str, any]:
        """Get current sound manager status for debugging."""
        return {
            "enabled": self.sounds_enabled,
            "volume": self.volume,
            "available_sounds": len(self.available_sounds),
            "total_sounds": len(self.DEFAULT_SOUNDS),
            "is_playing": self.is_playing()
        }
