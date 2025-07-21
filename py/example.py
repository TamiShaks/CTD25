import cv2
from img import Img


class KFChessBoard:
    def __init__(self, background_path):
        self.background_path = background_path
        self.canvas = None
        self.pieces = {}  # Dictionary to track pieces: {position: piece_info}
        self.square_size = 100  # Assuming 100x100 pixel squares
        self.board_offset_x = 0  # Offset from left edge to board start
        self.board_offset_y = 0  # Offset from top edge to board start
    
    def load_board(self):
        """Load the background board image"""
        self.canvas = Img().read(self.background_path)
        return self.canvas
    
    def position_to_coordinates(self, row, col):
        """Convert board position (row, col) to pixel coordinates"""
        x = self.board_offset_x + (col * self.square_size)
        y = self.board_offset_y + (row * self.square_size)
        return x, y
    
    def place_piece(self, piece_path, row, col, piece_id=None):
        """Place a piece at the specified board position"""
        # Load the piece image
        piece = Img().read(piece_path,
                          size=(self.square_size, self.square_size),
                          keep_aspect=True,
                          interpolation=cv2.INTER_AREA)
        
        # Get pixel coordinates
        x, y = self.position_to_coordinates(row, col)
        
        # Store piece information
        position = (row, col)
        self.pieces[position] = {
            'piece_path': piece_path,
            'piece_id': piece_id,
            'coordinates': (x, y)
        }
        
        # Draw the piece on the canvas
        piece.draw_on(self.canvas, x, y)
        
        return True
    
    def replace_piece(self, old_row, old_col, new_piece_path, new_row=None, new_col=None, piece_id=None):
        """
        Replace a piece on the board
        If new_row and new_col are not provided, replaces piece at the same position
        """
        # Use same position if new position not specified
        if new_row is None:
            new_row = old_row
        if new_col is None:
            new_col = old_col
        
        # Remove old piece from tracking
        old_position = (old_row, old_col)
        if old_position in self.pieces:
            del self.pieces[old_position]
        
        # Reload the clean board
        self.canvas = Img().read(self.background_path)
        
        # Redraw all remaining pieces (excluding the old position)
        for position, piece_info in self.pieces.items():
            if position != old_position:
                temp_piece = Img().read(piece_info['piece_path'],
                                      size=(self.square_size, self.square_size),
                                      keep_aspect=True,
                                      interpolation=cv2.INTER_AREA)
                temp_piece.draw_on(self.canvas, piece_info['coordinates'][0], piece_info['coordinates'][1])
        
        # Place the new piece
        self.place_piece(new_piece_path, new_row, new_col, piece_id)
        
        return True
    
    def remove_piece(self, row, col):
        """Remove a piece from the board"""
        position = (row, col)
        if position in self.pieces:
            del self.pieces[position]
            
            # Reload and redraw all remaining pieces
            self.canvas = Img().read(self.background_path)
            for pos, piece_info in self.pieces.items():
                temp_piece = Img().read(piece_info['piece_path'],
                                      size=(self.square_size, self.square_size),
                                      keep_aspect=True,
                                      interpolation=cv2.INTER_AREA)
                temp_piece.draw_on(self.canvas, piece_info['coordinates'][0], piece_info['coordinates'][1])
            return True
        return False
    
    def move_piece(self, from_row, from_col, to_row, to_col):
        """Move a piece from one position to another"""
        from_position = (from_row, from_col)
        
        if from_position in self.pieces:
            piece_info = self.pieces[from_position]
            
            # Replace the piece at the new position
            self.replace_piece(from_row, from_col, 
                             piece_info['piece_path'], 
                             to_row, to_col, 
                             piece_info['piece_id'])
            return True
        return False
    
    def show_board(self):
        """Display the current board state"""
        if self.canvas:
            self.canvas.show()
    
    def save_board(self, output_path):
        """Save the current board state to file"""
        if self.canvas:
            # Assuming your Img class has a save method
            # self.canvas.save(output_path)
            pass


def main():
    # Example usage
    board = KFChessBoard("../board.png")
    board.load_board()
    
    # Place initial pieces
    board.place_piece("../pieces/QW/states/jump/sprites/2.png", 0, 0, "white_queen")
    board.place_piece("../pieces/KB/states/idle/sprites/1.png", 7, 7, "black_king")
    
    # Replace a piece (e.g., pawn promotion)
    board.replace_piece(0, 0, "../pieces/RW/states/idle/sprites/1.png", piece_id="white_rook")
    
    # Move a piece
    board.move_piece(7, 7, 6, 6)
    
    # Show the board
    board.show_board()


if __name__ == "__main__":
    main()
