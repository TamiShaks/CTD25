# mock_img.py
# from img import Img

# class MockImg(Img):
#     """Headless Img that just records calls."""
#     traj     : list[tuple[int,int]]  = []   # every draw_on() position
#     txt_traj : list[tuple[tuple[int,int],str]] = []

#     def __init__(self):                     # override, no cv2 needed
#         """Initialize mock image with mock pixels."""
#         pass

#     # keep the method names identical to Img -------------------------
#     def read(self, path, *_, **__):
#         """Mock read method that pretends to load an image."""
#         pass

#     def draw_on(self, other, x, y):
#         """Record draw operation position."""
#         pass

#     def put_text(self, txt, x, y, font_size, *_, **__):
#         """Record text placement operation."""
#         pass

#     def show(self): 
#         """Do nothing for show operation."""
#         pass

#     # helper for tests
#     @classmethod
#     def reset(cls):
#         """Reset the recorded trajectories."""
#         pass 

# mock_img.py
from img import Img
from typing import List, Tuple

class MockImg(Img):
    """Headless Img that just records calls for testing."""
    traj: List[Tuple[int, int]] = []   # every draw_on() position
    txt_traj: List[Tuple[Tuple[int, int], str]] = []  # text positions and content

    def __init__(self):
        """Initialize mock image with mock pixels."""
        # Don't call super().__init__() to avoid OpenCV dependencies
        self.img = None
        self.width = 800
        self.height = 600
        self._create_mock_image()

    def _create_mock_image(self):
        """Create a mock image array without OpenCV."""
        import numpy as np
        # Create a simple mock image (BGRA format)
        self.img = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        self.img[:, :, 3] = 255  # Full alpha

    def read(self, path, *args, **kwargs):
        """Mock read method that pretends to load an image."""
        # Just create a smaller mock image to simulate loading
        import numpy as np
        size = kwargs.get('size', (64, 64))
        width, height = size
        
        self.img = np.zeros((height, width, 4), dtype=np.uint8)
        # Create a colored square based on path name for variety
        color_hash = hash(str(path)) % 256
        self.img[:, :, 0] = color_hash  # B
        self.img[:, :, 1] = (color_hash * 2) % 256  # G
        self.img[:, :, 2] = (color_hash * 3) % 256  # R
        self.img[:, :, 3] = 255  # A
        
        return self

    def draw_on(self, other, x, y):
        """Record draw operation position."""
        MockImg.traj.append((x, y))
        
        # Actually perform a mock draw operation
        if hasattr(other, 'img') and other.img is not None and self.img is not None:
            try:
                h, w = self.img.shape[:2]
                H, W = other.img.shape[:2]
                
                # Check bounds
                if y + h <= H and x + w <= W:
                    # Simple copy operation (no alpha blending for mock)
                    other.img[y:y + h, x:x + w] = self.img
            except Exception:
                pass  # Ignore errors in mock mode

    def put_text(self, txt, x, y, font_size, *args, **kwargs):
        """Record text placement operation."""
        MockImg.txt_traj.append(((x, y), txt))
        
        # Mock text rendering - just mark the position
        if self.img is not None:
            try:
                # Draw a simple rectangle where text would be
                text_width = len(txt) * int(font_size * 10)
                text_height = int(font_size * 20)
                
                H, W = self.img.shape[:2]
                end_x = min(x + text_width, W)
                end_y = min(y + text_height, H)
                
                if x < W and y < H:
                    self.img[y:end_y, x:end_x, :3] = [255, 255, 255]  # White rectangle
            except Exception:
                pass

    def show(self): 
        """Do nothing for show operation in mock mode."""
        print(f"MockImg: Would show image of size {self.img.shape if self.img is not None else 'None'}")

    def copy(self) -> "MockImg":
        """Create a copy of the mock image."""
        new_mock = MockImg()
        if self.img is not None:
            import numpy as np
            new_mock.img = self.img.copy()
        new_mock.width = self.width
        new_mock.height = self.height
        return new_mock

    # Helper methods for tests
    @classmethod
    def reset(cls):
        """Reset the recorded trajectories."""
        cls.traj.clear()
        cls.txt_traj.clear()

    @classmethod
    def get_draw_positions(cls) -> List[Tuple[int, int]]:
        """Get all recorded draw positions."""
        return cls.traj.copy()

    @classmethod
    def get_text_operations(cls) -> List[Tuple[Tuple[int, int], str]]:
        """Get all recorded text operations."""
        return cls.txt_traj.copy()

    @classmethod
    def get_last_draw_position(cls) -> Tuple[int, int]:
        """Get the last draw position."""
        return cls.traj[-1] if cls.traj else (0, 0)