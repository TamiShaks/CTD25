#!/usr/bin/env python3
"""
Debug Game Pieces for Promotion
================================

Check if actual game pieces have the right properties for promotion detection.
"""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

from It1_interfaces.PieceFactory import PieceFactory
from It1_interfaces.Board import Board
from It1_interfaces.ChessRulesValidator import ChessRulesValidator

def debug_piece_properties():
    """Debug actual piece properties to see if promotion detection works."""
    print("🔍 Debugging Actual Game Pieces...")
    
    # Create board and piece factory
    from It1_interfaces.img import Img
    import numpy as np
    
    # Create a dummy board image
    board_img = Img()
    board_img.img = np.zeros((480, 480, 3), dtype=np.uint8)  # 8x8 board, 60px per cell
    
    board = Board(60, 60, 8, 8, board_img)
    piece_factory = PieceFactory(board, Path("pieces"))
    validator = ChessRulesValidator()
    
    print("\n📦 Creating test pawns...")
    
    # Create white pawn
    white_pawn = piece_factory.create_piece("PW", (6, 4))  # Start near promotion
    if white_pawn:
        print(f"✅ White pawn created: {white_pawn.piece_id}")
        print(f"   - piece_type: {getattr(white_pawn, 'piece_type', 'MISSING')}")
        print(f"   - color: {getattr(white_pawn, 'color', 'MISSING')}")
        
        # Test promotion detection
        promotion_test = validator.is_pawn_promotion(white_pawn, (0, 4))
        print(f"   - Promotion test to (0,4): {promotion_test}")
    else:
        print("❌ Failed to create white pawn")
    
    # Create black pawn  
    black_pawn = piece_factory.create_piece("PB", (1, 4))  # Start near promotion
    if black_pawn:
        print(f"✅ Black pawn created: {black_pawn.piece_id}")
        print(f"   - piece_type: {getattr(black_pawn, 'piece_type', 'MISSING')}")
        print(f"   - color: {getattr(black_pawn, 'color', 'MISSING')}")
        
        # Test promotion detection
        promotion_test = validator.is_pawn_promotion(black_pawn, (7, 4))
        print(f"   - Promotion test to (7,4): {promotion_test}")
    else:
        print("❌ Failed to create black pawn")

def debug_pawn_files():
    """Check what pawn files exist."""
    print("\n📂 Checking pawn piece files...")
    
    pieces_dir = Path("pieces")
    if not pieces_dir.exists():
        print("❌ Pieces directory not found!")
        return
    
    for pawn_dir in ["PW", "PB"]:
        pawn_path = pieces_dir / pawn_dir
        if pawn_path.exists():
            print(f"✅ {pawn_dir} directory exists")
            files = list(pawn_path.glob("*"))
            for file in files:
                print(f"   - {file.name}")
        else:
            print(f"❌ {pawn_dir} directory missing")

if __name__ == "__main__":
    print("🎯 PIECE PROPERTIES DEBUG TEST")
    print("=" * 50)
    
    debug_pawn_files()
    debug_piece_properties()
    
    print("\n💡 Next steps if pieces are created correctly:")
    print("   1. Add debug prints to ThreadedInputManager._execute_validated_move")
    print("   2. Check if chess_validator.is_pawn_promotion is being called")
    print("   3. See if promotion commands are reaching Game._handle_promotion_command")
