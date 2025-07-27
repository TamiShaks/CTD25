"""
Create a simple board image for the chess game
"""
import numpy as np
import cv2

def create_simple_board():
    """Create a simple chess board image"""
    board_size = 512
    cell_size = 64
    
    # Create empty board
    board = np.zeros((board_size, board_size, 3), dtype=np.uint8)
    
    # Create checkered pattern
    for row in range(8):
        for col in range(8):
            # Alternate between light and dark squares
            if (row + col) % 2 == 0:
                color = [240, 217, 181]  # Light brown
            else:
                color = [181, 136, 99]   # Dark brown
            
            y1, y2 = row * cell_size, (row + 1) * cell_size
            x1, x2 = col * cell_size, (col + 1) * cell_size
            board[y1:y2, x1:x2] = color
    
    # Add border
    cv2.rectangle(board, (0, 0), (board_size-1, board_size-1), (0, 0, 0), 2)
    
    # Save the board
    cv2.imwrite("board.png", board)
    print("✅ Created board.png")

if __name__ == "__main__":
    create_simple_board()
