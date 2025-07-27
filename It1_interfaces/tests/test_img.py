import sys
import os
import numpy as np
import pathlib

# הוספת הנתיב של It1_interfaces אל נתיב החיפוש
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from img import Img

def test_img_read_missing_file_creates_default():
    """Should create a default image when file does not exist."""
    path = pathlib.Path("nonexistent.png")
    img = Img().read(path, size=(10, 20))
    assert img.img.shape == (20, 10, 4)

def test_img_copy_independent():
    """Should return a true independent copy of the image."""
    i1 = Img()
    i1.img = np.ones((2, 2, 4), dtype=np.uint8) * 200
    copy_i1 = i1.copy()
    copy_i1.img[0, 0] = [0, 0, 0, 0]
    assert not np.array_equal(i1.img, copy_i1.img)
    
if __name__ == "__main__":
    test_img_read_missing_file_creates_default()
    test_img_copy_independent()
    print("All tests passed!")