# import pathlib
# import sys
# import cv2
# import numpy as np

# # Add the interfaces directory to path - go up one level from py folder
# project_root = pathlib.Path(__file__).parent.parent
# sys.path.append(str(project_root / "It1_interfaces"))

# from img import Img
# from Board import Board

# class KungFuChessGame:
#     def __init__(self):
#         # Set paths relative to project root
#         self.project_root = pathlib.Path(__file__).parent.parent
#         self.board_image_path = self.project_root / "board.png"
#         self.pieces_dir = self.project_root / "pieces"
        
#         # Board configuration
#         self.square_size = 100
#         self.board_size = 8
#         self.canvas = None
#         self.pieces = {}
        
#     def load_board(self):
#         """Load the chess board background"""
#         try:
#             self.canvas = Img().read(str(self.board_image_path))
#             print("✅ Board loaded successfully!")
#             return True
#         except Exception as e:
#             print(f"❌ Error loading board: {e}")
#             # Create a default checkered board
#             self.create_default_board()
#             return False
    
#     def create_default_board(self):
#         """Create a default checkered board if board.png doesn't exist"""
#         board_pixel_size = self.square_size * self.board_size
        
#         # Create checkered pattern
#         board = np.zeros((board_pixel_size, board_pixel_size, 3), dtype=np.uint8)
        
#         for row in range(self.board_size):
#             for col in range(self.board_size):
#                 # Alternate colors
#                 if (row + col) % 2 == 0:
#                     color = (240, 217, 181)  # Light squares (beige)
#                 else:
#                     color = (181, 136, 99)   # Dark squares (brown)
                
#                 y1 = row * self.square_size
#                 y2 = (row + 1) * self.square_size
#                 x1 = col * self.square_size
#                 x2 = (col + 1) * self.square_size
                
#                 board[y1:y2, x1:x2] = color
        
#         # Convert to Img object
#         self.canvas = Img()
#         self.canvas.data = board
#         print("✅ Default checkered board created!")
    
#     def position_to_coordinates(self, row, col):
#         """Convert board position to pixel coordinates"""
#         x = col * self.square_size+6
#         y = row * self.square_size
#         return x, y
    
#     def place_piece(self, piece_type, color, row, col):
#         """Place a piece on the board"""
#         # Build piece path
#         piece_code = f"{piece_type}{color}"  # e.g., "QW" for white queen
#         piece_path = self.pieces_dir / piece_code / "states" / "idle" / "sprites" / "1.png"
        
#         try:
#             if not piece_path.exists():
#                 print(f"⚠️  Warning: Piece image not found: {piece_path}")
#                 return False
            
#             # Load piece image
#             piece = Img().read(str(piece_path),
#                               size=(self.square_size, self.square_size),
#                               keep_aspect=True,
#                               interpolation=cv2.INTER_AREA)
            
#             # Get coordinates
#             x, y = self.position_to_coordinates(row, col)
            
#             # Draw piece on board
#             piece.draw_on(self.canvas, x, y)
            
#             # Store piece info
#             self.pieces[(row, col)] = {
#                 'type': piece_type,
#                 'color': color,
#                 'path': str(piece_path)
#             }
            
#             print(f"✅ Placed {piece_type}{color} at ({row}, {col})")
#             return True
            
#         except Exception as e:
#             print(f"❌ Error placing piece {piece_type}{color}: {e}")
#             return False
    
#     def setup_initial_position(self):
#         """Set up the initial chess position"""
#         print("Setting up initial chess position...")
        
#         # Define piece types and their positions
#         piece_order = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        
#         # Place white pieces (bottom of board)
#         for col, piece_type in enumerate(piece_order):
#             self.place_piece(piece_type, 'W', 7, col)  # Back rank
#             self.place_piece('P', 'W', 6, col)         # Pawns
        
#         # Place black pieces (top of board)  
#         for col, piece_type in enumerate(piece_order):
#             self.place_piece(piece_type, 'B', 0, col)  # Back rank
#             self.place_piece('P', 'B', 1, col)         # Pawns
    
#     def show_board(self):
#         """Display the board"""
#         if self.canvas:
#             self.canvas.show()
#             print("🎯 Board displayed! Press any key on the image window to continue, 'q' to quit")
#         else:
#             print("❌ No board to display")
    
#     # def run_demo(self):
#     #     """Run a demonstration"""
#     #     print("🥋 Starting Kung Fu Chess Demo! 🥋")
        
#     #     # Load or create board
#     #     self.load_board()
        
#     #     # Set up pieces
#     #     self.setup_initial_position()
        
#     #     # Show the board
#     #     self.show_board()
        
#     #     # Wait for user input
#     #     key = cv2.waitKey(0)
        
#     #     # Clean up
#     #     cv2.destroyAllWindows()
        
#     #     if key == ord('q') or key == 27:  # 'q' or ESC
#     #         print("🎯 Demo ended. Thanks for watching!")
        
#     #     return True

# def run_game_loop(self):
#     print("🥋 Starting Kung Fu Chess Game Loop! 🥋")
#     self.load_board()
#     self.setup_initial_position()
    
#     import time
#     import cv2

#     start_time = int(time.time() * 1000)
#     pieces_list = list(self.pieces.values())

#     while True:
#         now = int(time.time() * 1000) - start_time
        
#         # עדכון מצב
#         for info in pieces_list:
#             piece = info['piece']
#             piece.update(now)
        
#         # שרטוט מחדש
#         self.create_default_board()  # נקה את הלוח
#         for info in pieces_list:
#             piece = info['piece']
#             piece.draw_on_board(self, now)
        
#         self.canvas.show("Kung Fu Chess")
        
#         key = cv2.waitKey(30)
#         if key == ord('q') or key == 27:
#             break

#     cv2.destroyAllWindows()

# def main():
#     """Main function"""
#     try:
#         game = KungFuChessGame()
#         # game.run_demo()
#         game.run_game_loop()
#         print("🎯 Game loop ended. Thanks for playing!")
#     except Exception as e:
#         print(f"❌ Error running game: {e}")
#         import traceback
#         traceback.print_exc()


# if __name__ == "__main__":
#     main()
import pathlib
import sys
import cv2
import numpy as np
import time

# Add the interfaces directory to path - go up one level from py folder
project_root = pathlib.Path(__file__).parent.parent
sys.path.append(str(project_root / "It1_interfaces"))

from img import Img
from Board import Board
from PieceFactory import PieceFactory

class KungFuChessGame:
    def __init__(self):
        # Set paths relative to project root
        self.project_root = pathlib.Path(__file__).parent.parent
        self.board_image_path = self.project_root / "board.png"
        self.pieces_dir = self.project_root / "pieces"

        # Board configuration
        self.square_size = 100
        self.board_size = 8

        # Load board image
        background_img = Img().read(str(self.board_image_path))
        if background_img.img is None:
            raise FileNotFoundError(f"Could not load board image from: {self.board_image_path}")

        # Init board and piece factory
        self.board = Board(
            cell_H_pix=self.square_size,
            cell_W_pix=self.square_size,
            W_cells=self.board_size,
            H_cells=self.board_size,
            img=background_img
        )
        self.piece_factory = PieceFactory(self.board, self.pieces_dir)

        # Dictionary of all active pieces
        self.pieces = {}

    def setup_initial_position(self):
        print("Setting up initial chess position...")
        piece_order = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']

        for col, piece_type in enumerate(piece_order):
            white_piece = self.piece_factory.create_piece(piece_type + 'W', (7, col))
            white_piece.reset(0)
            self.pieces[(7, col)] = white_piece

            white_pawn = self.piece_factory.create_piece('PW', (6, col))
            white_pawn.reset(0)
            self.pieces[(6, col)] = white_pawn

            black_piece = self.piece_factory.create_piece(piece_type + 'B', (0, col))
            black_piece.reset(0)
            self.pieces[(0, col)] = black_piece

            black_pawn = self.piece_factory.create_piece('PB', (1, col))
            black_pawn.reset(0)
            self.pieces[(1, col)] = black_pawn

    def run_game_loop(self):
        print("\n🥋 Starting Kung Fu Chess Game Loop! 🥋")
        self.board.reset_board()
        self.setup_initial_position()

        start_time = int(time.time() * 1000)
        while True:
            now = int(time.time() * 1000) - start_time

            # Update each piece
            for piece in self.pieces.values():
                piece.update(now)

            # Redraw board
            self.board.reset_board()
            for piece in self.pieces.values():
                piece.draw_on_board(self.board, now)

            self.board.img.show("Kung Fu Chess")
            key = cv2.waitKey(30)
            if key == ord('q') or key == 27:
                break

        cv2.destroyAllWindows()


def main():
    try:
        game = KungFuChessGame()
        game.run_game_loop()
        print("\n🎯 Game loop ended. Thanks for playing!")
    except Exception as e:
        print(f"❌ Error running game: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
