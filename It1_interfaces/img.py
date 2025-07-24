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
            # Read image with alpha channel
            self.img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
            if self.img is None:
                self.img = cv2.imread(str(path), cv2.IMREAD_COLOR)

            if self.img is None:
                # Create a default colored rectangle if image not found
                if size:
                    w, h = size
                else:
                    w, h = 64, 64

                self.img = np.zeros((h, w, 4), dtype=np.uint8)
                # Create a colored square based on filename for variety
                color_hash = hash(str(path)) % 256
                self.img[:, :, 0] = color_hash  # B
                self.img[:, :, 1] = (color_hash * 2) % 256  # G
                self.img[:, :, 2] = (color_hash * 3) % 256  # R
                self.img[:, :, 3] = 255  # A
            else:

                # Convert to BGRA if needed
                if len(self.img.shape) == 3:
                    if self.img.shape[2] == 3:
                        alpha = np.ones((self.img.shape[0], self.img.shape[1], 1), dtype=self.img.dtype) * 255
                        self.img = np.concatenate([self.img, alpha], axis=2)

                # Resize if needed
                if size:
                    self.img = cv2.resize(self.img, size)

            if self.img is not None:
                self.height, self.width = self.img.shape[:2]

        except Exception as e:
            # Create default image
            if size:
                w, h = size
            else:
                w, h = 64, 64
            self.img = np.zeros((h, w, 4), dtype=np.uint8)
            self.img[:, :] = [128, 128, 128, 255]  # Gray default
            self.width, self.height = w, h
        
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

            src_region = self.img[src_y1:src_y2, src_x1:src_x2].astype(float)
            dst_region = target_img[dst_y1:dst_y2, dst_x1:dst_x2].astype(float)

            # Extract alpha channel normalized [0..1]
            alpha = src_region[:, :, 3] / 255.0
            alpha = alpha[:, :, None]  # Make it broadcastable

            # Blend all color channels at once using vectorized operations
            dst_region[:, :, :3] = alpha * src_region[:, :, :3] + (1 - alpha) * dst_region[:, :, :3]

            # Set alpha to max between source and destination (optional)
            dst_region[:, :, 3] = np.maximum(src_region[:, :, 3], dst_region[:, :, 3])

            # Write back to target (convert back to uint8)
            target_img[dst_y1:dst_y2, dst_x1:dst_x2] = dst_region.astype(np.uint8)

        except Exception as e:
            pass
        finally:
            pass


    def copy(self) -> "Img":
        """Create a copy of this image."""
        new_img = Img()
        if self.img is not None:
            new_img.img = self.img.copy()
            new_img.width = self.width
            new_img.height = self.height
        return new_img

    def show(self, window_name: str = "Image"):
        """Show the image in a window."""
        if self.img is not None:
            cv2.imshow(window_name, self.img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()