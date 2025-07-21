# import pathlib
# from dataclasses import dataclass, field
# from typing import List, Dict, Tuple, Optional
# import copy
# from img import Img
# from Command import Command



# class Graphics:
#     def __init__(self,
#                  sprites_folder: pathlib.Path,
#                  cell_size: tuple[int, int],        # NEW
#                  loop: bool = True,
#                  fps: float = 6.0):
#         """Initialize graphics with sprites folder, cell size, loop setting, and FPS."""
#         pass

#     def copy(self):
#         """Create a shallow copy of the graphics object."""
#         pass

#     def reset(self, cmd: Command):
#         """Reset the animation with a new command."""
#         pass

#     def update(self, now_ms: int):
#         """Advance animation frame based on game-loop time, not wall time."""
#         pass

#     def get_img(self) -> Img:
#         """Get the current frame image."""
#         pass 

import pathlib
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import copy
from img import Img
from Command import Command

class Graphics:
    def __init__(self, sprites_folder: pathlib.Path, cell_size: tuple[int, int], loop: bool = True, fps: float = 6.0):
        """Initialize graphics with sprites folder, cell size, loop setting, and FPS."""
        self.sprites_folder = sprites_folder
        self.cell_size = cell_size
        self.loop = loop
        self.fps = fps
        self.frame_duration_ms = int(1000.0 / fps)
        
        # Animation state
        self.sprites: List[Img] = []
        self.current_frame = 0
        self.animation_start_time = 0
        self.is_playing = False
        self.current_command = None
        
        self._load_sprites()

    def _load_sprites(self):
        """Load all sprite images from the sprites folder."""
        self.sprites = []
        if not self.sprites_folder.exists():
            return
            
        # Load sprites in numerical order
        sprite_files = []
        for file in self.sprites_folder.glob("*.png"):
            try:
                frame_num = int(file.stem)
                sprite_files.append((frame_num, file))
            except ValueError:
                sprite_files.append((999, file))  # Non-numeric files go last
                
        sprite_files.sort()
        
        for _, sprite_file in sprite_files:
            try:
                sprite = Img().read(
                    sprite_file, 
                    size=self.cell_size, 
                    keep_aspect=True
                )
                self.sprites.append(sprite)
            except Exception as e:
                print(f"Warning: Could not load sprite {sprite_file}: {e}")
        
        if not self.sprites:
            # Create a default sprite if no sprites found
            default_sprite = Img()
            # Create a simple colored rectangle as default
            import numpy as np
            import cv2
            default_img = np.zeros((self.cell_size[1], self.cell_size[0], 4), dtype=np.uint8)
            default_img[:] = [255, 0, 255, 255]  # Magenta
            default_sprite.img = default_img
            self.sprites.append(default_sprite)

    def copy(self):
        """Create a shallow copy of the graphics object."""
        new_graphics = Graphics(
            self.sprites_folder,
            self.cell_size,
            self.loop,
            self.fps
        )
        new_graphics.sprites = self.sprites.copy()
        new_graphics.current_frame = self.current_frame
        new_graphics.animation_start_time = self.animation_start_time
        new_graphics.is_playing = self.is_playing
        new_graphics.current_command = self.current_command
        return new_graphics

    def reset(self, cmd: Command):
        """Reset the animation with a new command."""
        self.current_command = cmd
        self.current_frame = 0
        self.animation_start_time = cmd.timestamp
        self.is_playing = True

    def update(self, now_ms: int):
        """Advance animation frame based on game-loop time, not wall time."""
        if not self.is_playing or not self.sprites:
            return
            
        elapsed = now_ms - self.animation_start_time
        frame_index = int(elapsed / self.frame_duration_ms)
        
        if frame_index >= len(self.sprites):
            if self.loop:
                frame_index = frame_index % len(self.sprites)
            else:
                frame_index = len(self.sprites) - 1
                self.is_playing = False
                
        self.current_frame = frame_index

    def get_img(self) -> Img:
        """Get the current frame image."""
        if not self.sprites:
            # Return empty image if no sprites
            empty = Img()
            import numpy as np
            empty.img = np.zeros((self.cell_size[1], self.cell_size[0], 4), dtype=np.uint8)
            return empty
            
        return self.sprites[self.current_frame]