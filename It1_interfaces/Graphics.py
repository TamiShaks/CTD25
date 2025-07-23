import pathlib
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import copy
from .img import Img
from .Command import Command

class Graphics:
    def __init__(self, sprites_folder: pathlib.Path, cell_size: tuple[int, int], 
                 loop: bool = True, fps: float = 6.0):
        """Initialize graphics with sprites folder, cell size, loop setting, and FPS."""
        self.sprites_folder = sprites_folder
        self.cell_size = cell_size
        self.loop = loop
        self.fps = fps
        self.frame_duration_ms = int(1000 / fps)
        
        # Load sprites
        self.frames = []
        if sprites_folder.exists():
            sprite_files = sorted([f for f in sprites_folder.iterdir() 
                                 if f.suffix.lower() in ['.png', '.jpg', '.jpeg']])
            
            for sprite_file in sprite_files:
                img = Img().read(sprite_file, size=cell_size, keep_aspect=True)
                self.frames.append(img)
        
        self.current_frame = 0
        self.animation_start_time = 0
        self.current_command = None

    def copy(self):
        """Create a shallow copy of the graphics object."""
        new_graphics = Graphics(self.sprites_folder, self.cell_size, self.loop, self.fps)
        new_graphics.frames = self.frames.copy()
        new_graphics.current_frame = self.current_frame
        new_graphics.animation_start_time = self.animation_start_time
        new_graphics.current_command = self.current_command
        return new_graphics

    def reset(self, cmd: Command):
        """Reset the animation with a new command."""
        self.current_command = cmd
        self.animation_start_time = cmd.timestamp
        self.current_frame = 0

    def update(self, now_ms: int):
        """Advance animation frame based on game-loop time, not wall time."""
        if not self.frames or not self.current_command:
            return
            
        elapsed = now_ms - self.animation_start_time
        frame_index = int(elapsed / self.frame_duration_ms)
        
        if self.loop:
            self.current_frame = frame_index % len(self.frames)
        else:
            self.current_frame = min(frame_index, len(self.frames) - 1)

    def get_img(self) -> Img:
        """Get the current frame image."""
        if self.frames:
            return self.frames[self.current_frame]
        else:
            # Return empty image if no frames
            empty = Img()
            empty.img = np.zeros((*self.cell_size[::-1], 4), dtype=np.uint8)
            return empty

