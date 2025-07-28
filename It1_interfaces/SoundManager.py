import pygame
import os
from It1_interfaces.EventTypes import MOVE_DONE, PIECE_CAPTURED, GAME_ENDED, GAME_STARTED, INVALID_MOVE

class SoundManager:
    def __init__(self):
        try:
            pygame.mixer.init()
            self.sounds_enabled = True
            self.sounds = {
                MOVE_DONE: "sounds/5movement0.wav",
                PIECE_CAPTURED: "sounds/gan.wav",
                GAME_ENDED: "sounds/applause.mp3",
                GAME_STARTED: "sounds/1TADA.WAV",
                INVALID_MOVE: "sounds/fail.mp3"
            }
            
            # Check which sound files actually exist
            self.available_sounds = {}
            for event_type, sound_file in self.sounds.items():
                if os.path.exists(sound_file):
                    self.available_sounds[event_type] = sound_file
            
        except Exception as e:
            self.sounds_enabled = False
            self.available_sounds = {}

    def update(self, event_type, data):
        if not self.sounds_enabled:
            return
            
        sound_file = self.available_sounds.get(event_type)
        if sound_file:
            try:
                # Stop any currently playing sound first
                pygame.mixer.music.stop()
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.play()
            except Exception as e:
                pass
    
    def play_custom_sound(self, sound_file):
        """Play a custom sound file."""
        if not self.sounds_enabled:
            return False
            
        try:
            if os.path.exists(sound_file):
                pygame.mixer.music.stop()
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.play()
                return True
            else:
                return False
        except Exception as e:
            return False
