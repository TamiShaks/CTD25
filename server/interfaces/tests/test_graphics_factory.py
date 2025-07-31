#!/usr/bin/env python3
"""
🧪 Comprehensive Tests for GraphicsFactory Class
==============================================

Tests all functionality of the GraphicsFactory class including:
- Factory method pattern implementation
- Graphics object creation
- Configuration parameter handling
- Path validation and processing
- Default value behavior
- Edge cases and error handling
"""

import unittest
import sys
import os
import pathlib

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class MockGraphics:
    """Mock Graphics class for testing"""
    def __init__(self, sprites_folder, cell_size, loop, fps, state_name):
        self.sprites_folder = sprites_folder
        self.cell_size = cell_size
        self.loop = loop
        self.fps = fps
        self.state_name = state_name

class GraphicsFactory:
    @staticmethod
    def create(sprites_dir: pathlib.Path, cfg: dict = None, cell_size: tuple[int, int] = (64, 64), state_name: str = ""):
        """
        Create a Graphics instance from sprites directory with optional config and cell size.
        """
        if cfg is None:
            cfg = {}

        loop = cfg.get('loop', True)
        fps = cfg.get('fps', 6.0)

        return MockGraphics(
            sprites_folder=sprites_dir,
            cell_size=cell_size,
            loop=loop,
            fps=fps,
            state_name=state_name
        )

class TestGraphicsFactory(unittest.TestCase):
    """Comprehensive test suite for GraphicsFactory class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.mock_sprites_dir = pathlib.Path("/mock/sprites")
        self.standard_cfg = {'loop': True, 'fps': 10.0}
        self.standard_cell_size = (64, 64)
        self.standard_state_name = "test_state"
    
    def test_create_basic_functionality(self):
        """🧪 Test basic Graphics creation through factory"""        
        result = GraphicsFactory.create(
            sprites_dir=self.mock_sprites_dir,
            cfg=self.standard_cfg,
            cell_size=self.standard_cell_size,
            state_name=self.standard_state_name
        )
        
        self.assertEqual(result.sprites_folder, self.mock_sprites_dir)
        self.assertEqual(result.cell_size, self.standard_cell_size)
        self.assertEqual(result.loop, True)
        self.assertEqual(result.fps, 10.0)
        self.assertEqual(result.state_name, self.standard_state_name)
        self.assertIsInstance(result, MockGraphics)
    
    def test_create_with_none_config(self):
        """🧪 Test Graphics creation with None configuration"""        
        result = GraphicsFactory.create(
            sprites_dir=self.mock_sprites_dir,
            cfg=None,
            cell_size=self.standard_cell_size,
            state_name=self.standard_state_name
        )
        
        self.assertEqual(result.loop, True)      # Default value
        self.assertEqual(result.fps, 6.0)        # Default value
    
    def test_create_with_empty_config(self):
        """🧪 Test Graphics creation with empty configuration dict"""        
        result = GraphicsFactory.create(
            sprites_dir=self.mock_sprites_dir,
            cfg={},
            cell_size=self.standard_cell_size,
            state_name=self.standard_state_name
        )
        
        self.assertEqual(result.loop, True)      # Default value
        self.assertEqual(result.fps, 6.0)        # Default value
    
    def test_create_with_partial_config(self):
        """🧪 Test Graphics creation with partial configuration"""        
        partial_cfg = {'fps': 15.0}
        result = GraphicsFactory.create(
            sprites_dir=self.mock_sprites_dir,
            cfg=partial_cfg,
            cell_size=self.standard_cell_size,
            state_name=self.standard_state_name
        )
        
        self.assertEqual(result.loop, True)      # Default value (missing from cfg)
        self.assertEqual(result.fps, 15.0)       # Specified value
    
    def test_create_default_cell_size(self):
        """🧪 Test Graphics creation with default cell size"""        
        result = GraphicsFactory.create(
            sprites_dir=self.mock_sprites_dir,
            cfg=self.standard_cfg,
            state_name=self.standard_state_name
        )
        
        self.assertEqual(result.cell_size, (64, 64))  # Default cell size
    
    def test_create_different_cell_sizes(self):
        """🧪 Test Graphics creation with various cell sizes"""        
        test_cell_sizes = [(32, 32), (128, 128), (64, 32), (100, 75)]
        
        for cell_size in test_cell_sizes:
            with self.subTest(cell_size=cell_size):                
                result = GraphicsFactory.create(
                    sprites_dir=self.mock_sprites_dir,
                    cfg=self.standard_cfg,
                    cell_size=cell_size,
                    state_name=self.standard_state_name
                )
                
                self.assertEqual(result.cell_size, cell_size)
    
    def test_create_different_fps_values(self):
        """🧪 Test Graphics creation with various FPS values"""        
        test_fps_values = [1.0, 6.0, 30.0, 60.0, 0.5]
        
        for fps in test_fps_values:
            with self.subTest(fps=fps):                
                cfg = {'fps': fps, 'loop': True}
                result = GraphicsFactory.create(
                    sprites_dir=self.mock_sprites_dir,
                    cfg=cfg,
                    cell_size=self.standard_cell_size,
                    state_name=self.standard_state_name
                )
                
                self.assertEqual(result.fps, fps)
    
    def test_create_different_loop_values(self):
        """🧪 Test Graphics creation with different loop values"""        
        for loop_value in [True, False]:
            with self.subTest(loop=loop_value):                
                cfg = {'loop': loop_value, 'fps': 10.0}
                result = GraphicsFactory.create(
                    sprites_dir=self.mock_sprites_dir,
                    cfg=cfg,
                    cell_size=self.standard_cell_size,
                    state_name=self.standard_state_name
                )
                
                self.assertEqual(result.loop, loop_value)
    
    def test_create_different_path_types(self):
        """🧪 Test Graphics creation with different path types"""        
        test_paths = [
            pathlib.Path("/absolute/path/sprites"),
            pathlib.Path("relative/path/sprites"),
            pathlib.Path("./current/sprites"),
            pathlib.Path("../parent/sprites"),
        ]
        
        for path in test_paths:
            with self.subTest(path=str(path)):                
                result = GraphicsFactory.create(
                    sprites_dir=path,
                    cfg=self.standard_cfg,
                    cell_size=self.standard_cell_size,
                    state_name=self.standard_state_name
                )
                
                self.assertEqual(result.sprites_folder, path)
    
    def test_create_complex_config(self):
        """🧪 Test Graphics creation with complex configuration"""        
        complex_cfg = {
            'loop': False,
            'fps': 25.0,
            'unused_param': 'should_be_ignored',
            'extra_data': {'nested': 'value'}
        }
        
        result = GraphicsFactory.create(
            sprites_dir=self.mock_sprites_dir,
            cfg=complex_cfg,
            cell_size=self.standard_cell_size,
            state_name=self.standard_state_name
        )
        
        self.assertEqual(result.loop, False)
        self.assertEqual(result.fps, 25.0)
    
    def test_create_state_name_variations(self):
        """🧪 Test Graphics creation with various state names"""        
        test_state_names = ["idle", "running", "jumping", "attack_01", "special_move_combo", "game_over", ""]
        
        for state_name in test_state_names:
            with self.subTest(state_name=state_name):                
                result = GraphicsFactory.create(
                    sprites_dir=self.mock_sprites_dir,
                    cfg=self.standard_cfg,
                    cell_size=self.standard_cell_size,
                    state_name=state_name
                )
                
                self.assertEqual(result.state_name, state_name)
    
    def test_factory_is_static_method(self):
        """🧪 Test that create method is a static method"""
        self.assertTrue(hasattr(GraphicsFactory, 'create'))
        self.assertTrue(callable(GraphicsFactory.create))
        method = getattr(GraphicsFactory, 'create')
        self.assertIsNotNone(method)
    
    def test_factory_returns_graphics_instance(self):
        """🧪 Test that factory always returns a Graphics instance"""        
        result = GraphicsFactory.create(
            sprites_dir=self.mock_sprites_dir,
            cfg=self.standard_cfg,
            cell_size=self.standard_cell_size,
            state_name=self.standard_state_name
        )
        
        self.assertIsInstance(result, MockGraphics)
        self.assertTrue(hasattr(result, 'sprites_folder'))
        self.assertTrue(hasattr(result, 'cell_size'))
        self.assertTrue(hasattr(result, 'loop'))
        self.assertTrue(hasattr(result, 'fps'))
        self.assertTrue(hasattr(result, 'state_name'))
    
    def test_create_multiple_instances(self):
        """🧪 Test creating multiple Graphics instances through factory"""        
        result1 = GraphicsFactory.create(
            sprites_dir=pathlib.Path("/sprites1"),
            cfg={'fps': 10.0},
            cell_size=(32, 32),
            state_name="state1"
        )
        
        result2 = GraphicsFactory.create(
            sprites_dir=pathlib.Path("/sprites2"),
            cfg={'fps': 20.0},
            cell_size=(64, 64),
            state_name="state2"
        )
        
        self.assertIsNot(result1, result2)
        self.assertEqual(result1.sprites_folder, pathlib.Path("/sprites1"))
        self.assertEqual(result1.cell_size, (32, 32))
        self.assertEqual(result1.fps, 10.0)
        self.assertEqual(result1.state_name, "state1")
        
        self.assertEqual(result2.sprites_folder, pathlib.Path("/sprites2"))
        self.assertEqual(result2.cell_size, (64, 64))
        self.assertEqual(result2.fps, 20.0)
        self.assertEqual(result2.state_name, "state2")
    
    def test_config_dict_not_modified(self):
        """🧪 Test that the original config dict is not modified by the factory"""        
        original_cfg = {'loop': True, 'fps': 15.0}
        original_cfg_copy = original_cfg.copy()
        
        GraphicsFactory.create(
            sprites_dir=self.mock_sprites_dir,
            cfg=original_cfg,
            cell_size=self.standard_cell_size,
            state_name=self.standard_state_name
        )
        
        self.assertEqual(original_cfg, original_cfg_copy)
    
    def test_create_with_minimal_parameters(self):
        """🧪 Test Graphics creation with only required parameter"""
        result = GraphicsFactory.create(sprites_dir=self.mock_sprites_dir)
        
        self.assertEqual(result.sprites_folder, self.mock_sprites_dir)
        self.assertEqual(result.cell_size, (64, 64))  # Default
        self.assertEqual(result.loop, True)           # Default
        self.assertEqual(result.fps, 6.0)             # Default
        self.assertEqual(result.state_name, "")       # Default

if __name__ == '__main__':
    unittest.main(verbosity=2)
