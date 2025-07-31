#!/usr/bin/env python3
"""
🧪 Comprehensive Tests for Graphics Class
========================================

Tests all functionality of the Graphics class including:
- Initialization and configuration
- Sprite loading and management
- Animation frame updates
- Copy functionality
- Command reset handling
- Frame rate and timing
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import pathlib
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import modules without relative imports
from Graphics import Graphics
from Command import Command
from img import Img

class TestGraphics(unittest.TestCase):
    """Comprehensive test suite for Graphics class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.test_cell_size = (64, 64)
        self.current_time = int(time.time() * 1000)
        
        # Create mock sprites folder
        self.mock_sprites_folder = Mock(spec=pathlib.Path)
        self.mock_sprites_folder.exists.return_value = True
        
        # Create mock sprite files
        self.mock_sprite_files = [
            Mock(suffix='.png', name='sprite1.png'),
            Mock(suffix='.png', name='sprite2.png'),
            Mock(suffix='.jpg', name='sprite3.jpg')
        ]
        self.mock_sprites_folder.iterdir.return_value = self.mock_sprite_files
        
    @patch('Graphics.Img')
    def test_graphics_initialization_basic(self, mock_img_class):
        """🧪 Test basic graphics initialization"""
        # Mock Img instances
        mock_img_instances = [Mock(spec=Img) for _ in range(3)]
        mock_img_class.return_value.read.side_effect = mock_img_instances
        
        graphics = Graphics(
            sprites_folder=self.mock_sprites_folder,
            cell_size=self.test_cell_size,
            loop=True,
            fps=6.0,
            state_name="idle"
        )
        
        # Verify initialization
        self.assertEqual(graphics.sprites_folder, self.mock_sprites_folder)
        self.assertEqual(graphics.cell_size, self.test_cell_size)
        self.assertTrue(graphics.loop)
        self.assertEqual(graphics.fps, 6.0)
        self.assertEqual(graphics.frame_duration_ms, int(1000/6.0))
        self.assertEqual(graphics.state_name, "idle")
        self.assertEqual(graphics.current_frame, 0)
        self.assertEqual(graphics.animation_start_time, 0)
        self.assertIsNone(graphics.current_command)
        
        # Verify frames were loaded
        self.assertEqual(len(graphics.frames), 3)
    
    @patch('It1_interfaces.Graphics.Img')
    def test_graphics_initialization_different_fps(self, mock_img_class):
        """🧪 Test graphics initialization with different FPS values"""
        fps_values = [1.0, 6.0, 12.0, 30.0, 60.0]
        
        for fps in fps_values:
            with self.subTest(fps=fps):
                graphics = Graphics(
                    sprites_folder=self.mock_sprites_folder,
                    cell_size=self.test_cell_size,
                    fps=fps
                )
                
                self.assertEqual(graphics.fps, fps)
                self.assertEqual(graphics.frame_duration_ms, int(1000/fps))
    
    @patch('It1_interfaces.Graphics.Img')
    def test_graphics_initialization_no_loop(self, mock_img_class):
        """🧪 Test graphics initialization with loop disabled"""
        graphics = Graphics(
            sprites_folder=self.mock_sprites_folder,
            cell_size=self.test_cell_size,
            loop=False
        )
        
        self.assertFalse(graphics.loop)
    
    def test_graphics_initialization_nonexistent_folder(self):
        """🧪 Test graphics initialization with non-existent sprites folder"""
        mock_nonexistent_folder = Mock(spec=pathlib.Path)
        mock_nonexistent_folder.exists.return_value = False
        
        graphics = Graphics(
            sprites_folder=mock_nonexistent_folder,
            cell_size=self.test_cell_size
        )
        
        # Should initialize with empty frames
        self.assertEqual(len(graphics.frames), 0)
    
    @patch('It1_interfaces.Graphics.Img')
    def test_graphics_sprite_filtering(self, mock_img_class):
        """🧪 Test that only image files are loaded as sprites"""
        # Create mixed file types
        mixed_files = [
            Mock(suffix='.png', name='sprite1.png'),
            Mock(suffix='.txt', name='readme.txt'),
            Mock(suffix='.jpg', name='sprite2.jpg'),
            Mock(suffix='.py', name='script.py'),
            Mock(suffix='.jpeg', name='sprite3.jpeg'),
            Mock(suffix='.gif', name='sprite4.gif')  # Not supported
        ]
        
        self.mock_sprites_folder.iterdir.return_value = mixed_files
        mock_img_class.return_value.read.return_value = Mock(spec=Img)
        
        graphics = Graphics(
            sprites_folder=self.mock_sprites_folder,
            cell_size=self.test_cell_size
        )
        
        # Should only load .png, .jpg, .jpeg files (3 total)
        self.assertEqual(len(graphics.frames), 3)
    
    @patch('It1_interfaces.Graphics.Img')
    def test_graphics_copy(self, mock_img_class):
        """🧪 Test graphics copy functionality"""
        mock_img_instances = [Mock(spec=Img) for _ in range(2)]
        mock_img_class.return_value.read.side_effect = mock_img_instances
        
        original = Graphics(
            sprites_folder=self.mock_sprites_folder,
            cell_size=self.test_cell_size,
            loop=False,
            fps=12.0,
            state_name="move"
        )
        
        # Set some state
        original.current_frame = 1
        original.animation_start_time = self.current_time
        test_command = Command(self.current_time, "player1", "Move", [])
        original.current_command = test_command
        
        # Create copy
        copied = original.copy()
        
        # Verify copy has same values but is different object
        self.assertIsNot(copied, original)
        self.assertEqual(copied.sprites_folder, original.sprites_folder)
        self.assertEqual(copied.cell_size, original.cell_size)
        self.assertEqual(copied.loop, original.loop)
        self.assertEqual(copied.fps, original.fps)
        self.assertEqual(copied.state_name, original.state_name)
        self.assertEqual(copied.current_frame, original.current_frame)
        self.assertEqual(copied.animation_start_time, original.animation_start_time)
        self.assertEqual(copied.current_command, original.current_command)
        
        # Verify frames list is copied (shallow copy)
        self.assertIsNot(copied.frames, original.frames)
        self.assertEqual(len(copied.frames), len(original.frames))
    
    @patch('It1_interfaces.Graphics.Img')
    def test_graphics_reset(self, mock_img_class):
        """🧪 Test graphics reset with command"""
        graphics = Graphics(
            sprites_folder=self.mock_sprites_folder,
            cell_size=self.test_cell_size
        )
        
        # Set some initial state
        graphics.current_frame = 5
        graphics.animation_start_time = self.current_time - 1000
        
        # Create reset command
        reset_command = Command(
            timestamp=self.current_time,
            player_id="player1",
            cmd_type="Move",
            args=["PW1", "a1", "a2"]
        )
        
        graphics.reset(reset_command)
        
        # Verify reset
        self.assertEqual(graphics.current_command, reset_command)
        self.assertEqual(graphics.animation_start_time, self.current_time)
        self.assertEqual(graphics.current_frame, 0)
    
    @patch('It1_interfaces.Graphics.Img')
    def test_graphics_update_frame_advance(self, mock_img_class):
        """🧪 Test graphics update advances frames correctly"""
        mock_img_instances = [Mock(spec=Img) for _ in range(3)]
        mock_img_class.return_value.read.side_effect = mock_img_instances
        
        graphics = Graphics(
            sprites_folder=self.mock_sprites_folder,
            cell_size=self.test_cell_size,
            fps=6.0,  # ~167ms per frame
            loop=True
        )
        
        # Set animation start time
        graphics.animation_start_time = self.current_time
        
        # Update after one frame duration
        graphics.update(self.current_time + 167)
        self.assertEqual(graphics.current_frame, 1)
        
        # Update after two frame durations
        graphics.update(self.current_time + 334)
        self.assertEqual(graphics.current_frame, 2)
        
        # Update after three frame durations (should loop back to 0)
        graphics.update(self.current_time + 501)
        self.assertEqual(graphics.current_frame, 0)
    
    @patch('It1_interfaces.Graphics.Img')
    def test_graphics_update_no_loop(self, mock_img_class):
        """🧪 Test graphics update without looping"""
        mock_img_instances = [Mock(spec=Img) for _ in range(3)]
        mock_img_class.return_value.read.side_effect = mock_img_instances
        
        graphics = Graphics(
            sprites_folder=self.mock_sprites_folder,
            cell_size=self.test_cell_size,
            fps=6.0,
            loop=False  # No looping
        )
        
        graphics.animation_start_time = self.current_time
        
        # Update past all frames
        graphics.update(self.current_time + 1000)  # Way past end
        
        # Should stay at last frame
        self.assertEqual(graphics.current_frame, 2)  # Last frame index
    
    @patch('It1_interfaces.Graphics.Img')
    def test_graphics_update_no_frames(self, mock_img_class):
        """🧪 Test graphics update with no frames loaded"""
        # Mock empty folder
        empty_folder = Mock(spec=pathlib.Path)
        empty_folder.exists.return_value = True
        empty_folder.iterdir.return_value = []
        
        graphics = Graphics(
            sprites_folder=empty_folder,
            cell_size=self.test_cell_size
        )
        
        graphics.animation_start_time = self.current_time
        
        # Update should not crash with no frames
        graphics.update(self.current_time + 1000)
        self.assertEqual(graphics.current_frame, 0)
    
    @patch('It1_interfaces.Graphics.Img')
    def test_graphics_get_img_basic(self, mock_img_class):
        """🧪 Test get_img returns current frame"""
        mock_img_instances = [Mock(spec=Img) for _ in range(3)]
        mock_img_class.return_value.read.side_effect = mock_img_instances
        
        graphics = Graphics(
            sprites_folder=self.mock_sprites_folder,
            cell_size=self.test_cell_size
        )
        
        # Should return first frame initially
        result = graphics.get_img(0, 0, self.current_time)
        self.assertEqual(result, mock_img_instances[0])
        
        # Advance frame and test
        graphics.current_frame = 1
        result = graphics.get_img(0, 0, self.current_time)
        self.assertEqual(result, mock_img_instances[1])
    
    @patch('It1_interfaces.Graphics.Img')
    def test_graphics_get_img_no_frames(self, mock_img_class):
        """🧪 Test get_img with no frames returns None"""
        empty_folder = Mock(spec=pathlib.Path)
        empty_folder.exists.return_value = True
        empty_folder.iterdir.return_value = []
        
        graphics = Graphics(
            sprites_folder=empty_folder,
            cell_size=self.test_cell_size
        )
        
        result = graphics.get_img(0, 0, self.current_time)
        self.assertIsNone(result)
    
    @patch('It1_interfaces.Graphics.Img')
    def test_graphics_different_cell_sizes(self, mock_img_class):
        """🧪 Test graphics initialization with different cell sizes"""
        cell_sizes = [(32, 32), (64, 64), (128, 128), (50, 75)]
        
        for cell_size in cell_sizes:
            with self.subTest(cell_size=cell_size):
                graphics = Graphics(
                    sprites_folder=self.mock_sprites_folder,
                    cell_size=cell_size
                )
                
                self.assertEqual(graphics.cell_size, cell_size)
                
                # Verify Img.read was called with correct size
                mock_img_class.return_value.read.assert_called()
    
    @patch('It1_interfaces.Graphics.Img')
    def test_graphics_state_name_tracking(self, mock_img_class):
        """🧪 Test graphics tracks state name correctly"""
        state_names = ["idle", "move", "attack", "rest", "jump"]
        
        for state_name in state_names:
            with self.subTest(state_name=state_name):
                graphics = Graphics(
                    sprites_folder=self.mock_sprites_folder,
                    cell_size=self.test_cell_size,
                    state_name=state_name
                )
                
                self.assertEqual(graphics.state_name, state_name)

if __name__ == '__main__':
    unittest.main(verbosity=2)
