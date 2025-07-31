#!/usr/bin/env python3
"""
🧪 Simple Test for Img Class
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from img import Img

class TestImg(unittest.TestCase):
    """Simple test suite for Img class"""
    
    def test_img_initialization(self):
        """🧪 Test Img object initialization"""
        img = Img()
        
        self.assertIsNone(img.img)
        self.assertEqual(img.width, 0)
        self.assertEqual(img.height, 0)
        print("✅ Img initialization test passed!")

if __name__ == '__main__':
    unittest.main(verbosity=2)
