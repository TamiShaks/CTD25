#!/usr/bin/env python3
"""
Test file for MockImg functionality
קובץ בדיקה לפונקציונליות MockImg
"""

import sys
import pathlib

# Add interfaces to path
sys.path.append(str(pathlib.Path(__file__).parent / "It1_interfaces"))

from mock_img import MockImg


def test_mock_img():
    """Test MockImg basic functionality."""
    print("🧪 Testing MockImg...")
    
    # Reset trajectories
    MockImg.reset()
    
    # Test image creation and loading
    mock1 = MockImg()
    mock1.read("test_sprite.png", size=(64, 64))
    print(f"✓ Created mock image: {mock1.img.shape}")
    
    # Test drawing
    mock2 = MockImg()
    mock1.draw_on(mock2, 10, 20)
    print(f"✓ Draw recorded at: {MockImg.get_last_draw_position()}")
    
    # Test text
    mock2.put_text("Test Text", 50, 100, 2.0)
    text_ops = MockImg.get_text_operations()
    print(f"✓ Text recorded: {text_ops}")
    
    # Test trajectories
    draw_positions = MockImg.get_draw_positions()
    print(f"✓ All draw positions: {draw_positions}")
    
    print("🎉 MockImg tests completed successfully!")


if __name__ == "__main__":
    test_mock_img()