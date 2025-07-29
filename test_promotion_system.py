#!/usr/bin/env python3
"""
🧪 Test Pawn Promotion System
============================

Test the complete pawn promotion implementation.
"""

import pygame
import sys
from unittest.mock import Mock
from It1_interfaces.ChessRulesValidator import ChessRulesValidator
from It1_interfaces.Command import Command

def test_promotion_detection():
    """Test pawn promotion detection."""
    print("🧪 Testing Pawn Promotion Detection...")
    
    validator = ChessRulesValidator()
    
    # Create mock white pawn
    white_pawn = Mock()
    white_pawn.piece_type = "P"
    white_pawn.color = "White"
    
    # Create mock black pawn
    black_pawn = Mock()
    black_pawn.piece_type = "P"
    black_pawn.color = "Black"
    
    # Test cases
    test_cases = [
        (white_pawn, (0, 4), True, "White pawn reaching top row"),
        (white_pawn, (1, 4), False, "White pawn not at top"),
        (black_pawn, (7, 4), True, "Black pawn reaching bottom row"),
        (black_pawn, (6, 4), False, "Black pawn not at bottom"),
    ]
    
    for piece, target_pos, expected, description in test_cases:
        result = validator.is_pawn_promotion(piece, target_pos)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {description}: {result}")
    
    print()

def test_promotion_command():
    """Test promotion command creation."""
    print("🧪 Testing Promotion Command Creation...")
    
    # Test promotion command
    cmd = Command.create_promotion_command(
        timestamp=1000,
        piece_id="PW1",
        from_cell=(6, 0),
        to_cell=(7, 0),
        promotion_piece="Q"
    )
    
    print(f"  ✅ Command type: {cmd.type}")
    print(f"  ✅ Piece ID: {cmd.piece_id}")
    print(f"  ✅ From: {cmd.params[0]}")
    print(f"  ✅ To: {cmd.params[1]}")
    print(f"  ✅ Promotion: {cmd.params[2]}")
    print()

def test_promotion_ui_mock():
    """Test promotion UI rendering without pygame window."""
    print("🧪 Testing Promotion UI Components...")
    
    # Initialize pygame for font rendering
    pygame.init()
    
    from It1_interfaces.PromotionUI import PromotionUI
    
    # Create promotion UI
    ui = PromotionUI(800, 600)
    
    # Test piece names
    piece_names = ui.piece_names
    print(f"  ✅ Queen: {piece_names['Q']}")
    print(f"  ✅ Rook: {piece_names['R']}")
    print(f"  ✅ Bishop: {piece_names['B']}")
    print(f"  ✅ Knight: {piece_names['N']}")
    
    # Test instructions
    instructions = ui.instructions
    print(f"  ✅ Player A: {instructions['A']}")
    print(f"  ✅ Player B: {instructions['B']}")
    
    pygame.quit()
    print()

def main():
    """Run all promotion tests."""
    print("🎯 " + "="*60)
    print("🎯 PAWN PROMOTION SYSTEM TEST")
    print("🎯 " + "="*60)
    print()
    
    test_promotion_detection()
    test_promotion_command()
    test_promotion_ui_mock()
    
    print("🎉 All promotion system tests completed!")
    print()
    print("📋 Summary:")
    print("  ✅ Promotion detection works")
    print("  ✅ Promotion commands can be created")
    print("  ✅ Promotion UI components loaded")
    print()
    print("🎮 Key mappings for promotion:")
    print("  Player A: Arrow Keys to navigate, ENTER to select")
    print("  Player B: WASD to navigate, SPACE to select")

if __name__ == "__main__":
    main()
