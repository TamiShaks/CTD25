import cv2
import numpy as np
import pathlib
from typing import Optional, Tuple

class Img:
    def __init__(self):
        self.img: Optional[np.ndarray] = None
        self.width = 0
        self.height = 0

    def read(self, path: pathlib.Path, size: Optional[Tuple[int, int]] = None, keep_aspect: bool = True) -> "Img":
        """Read an image from file."""
        
        try:
            # Try to read image first
            if path.exists():
                self.img = cv2.imread(str(path), cv2.IMREAD_COLOR)  # Just load as BGR, no alpha
                
                if self.img is not None:
                    
                    # Resize if needed
                    if size:
                        self.img = cv2.resize(self.img, size)
                    
                    self.height, self.width = self.img.shape[:2]
                    return self
            
            # If we get here, file doesn't exist or couldn't load
            if size:
                w, h = size
            else:
                w, h = 64, 64
            
            # Create simple fallback (much smaller if memory issues)
            self.img = np.full((h, w, 3), 128, dtype=np.uint8)
            self.height, self.width = h, w
            
        except Exception as e:
            print(f"[ERROR] Exception in image loading: {e}")
            # Minimal fallback
            self.img = np.full((64, 64, 3), 128, dtype=np.uint8)
            self.height, self.width = 64, 64
        
        return self
    def draw_on(self, target: "Img", x: int, y: int):
        """Draw this image on another image at the specified position with alpha blending."""
        if isinstance(target, np.ndarray):
            target_img = target
        elif isinstance(target, Img):
            target_img = target.img
        else:
            return

        if self.img is None or target_img is None:
            return

        try:
            src_h, src_w = self.img.shape[:2]
            dst_h, dst_w = target_img.shape[:2]

            # Check bounds
            if x >= dst_w or y >= dst_h or x + src_w <= 0 or y + src_h <= 0:
                return

            # Calculate valid regions
            src_x1 = max(0, -x)
            src_y1 = max(0, -y)
            src_x2 = min(src_w, dst_w - x)
            src_y2 = min(src_h, dst_h - y)

            dst_x1 = max(0, x)
            dst_y1 = max(0, y)
            dst_x2 = dst_x1 + (src_x2 - src_x1)
            dst_y2 = dst_y1 + (src_y2 - src_y1)

            if src_x2 <= src_x1 or src_y2 <= src_y1:
                return

            # Simple copy without alpha blending to avoid memory issues
            src_region = self.img[src_y1:src_y2, src_x1:src_x2]
            target_img[dst_y1:dst_y2, dst_x1:dst_x2] = src_region

        except Exception as e:
            pass


    def copy(self) -> "Img":
        """Create a copy of this image."""
        new_img = Img()
        if self.img is not None:
            new_img.img = self.img.copy()
            new_img.width = self.width
            new_img.height = self.height
        return new_img

    def apply_blue_tint(self, intensity: float = 1.0) -> "Img":
        """Apply a blue tint to the image (for rest state) with variable intensity.
        
        Args:
            intensity: Tint intensity from 0.0 (no tint) to 1.0 (full tint)
        """
        if self.img is not None:
            # Clamp intensity to valid range
            intensity = max(0.0, min(1.0, intensity))
            
            # If intensity is 0, return original image
            if intensity == 0.0:
                return self.copy()
            
            # Create a copy first
            tinted = self.copy()
            
            # Convert to float for calculations
            img_float = tinted.img.astype(np.float32)
            original_float = img_float.copy()
            
            # OpenCV uses BGR format: [Blue, Green, Red]
            # Enhance blue channel and reduce red/green based on intensity
            img_float[:, :, 0] = np.minimum(img_float[:, :, 0] * (1.0 + 0.8 * intensity) + 80 * intensity, 255)  # Enhance Blue
            img_float[:, :, 1] = img_float[:, :, 1] * (1.0 - 0.7 * intensity)  # Reduce Green  
            img_float[:, :, 2] = img_float[:, :, 2] * (1.0 - 0.7 * intensity)  # Reduce Red
            
            # Convert back to uint8
            tinted.img = img_float.astype(np.uint8)
            return tinted
        else:
            return self.copy()

    def show(self, window_name: str = "Image"):
        """Show the image in a window."""
        if self.img is not None:
            cv2.imshow(window_name, self.img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
