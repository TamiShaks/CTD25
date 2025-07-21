#!/usr/bin/env python3
"""
Enhanced Kung Fu Chess Game with Visual Controls
- Arrow Keys: Player A (Red selection)
- WASD Keys: Player B (Blue selection)
- Enter: Move selected piece
"""

import pathlib
import sys
from typing import List, Tuple, Optional
import pygame
import time

# Add the It1_interfaces directory to the path
current_dir = pathlib.Path(__file__).parent
interfaces_dir = current_dir.parent / "It1_interfaces"
sys.path.append(str(interfaces_dir))

# Also add the project root to access pieces folder
project_root = current_dir.parent
sys.path.append(str(project_root))

from Board import Board
from Game import Game
from PieceFactory import PieceFactory
from Piece import Piece
from img import Img

class PlayerSelection:
    """Handles player selection and movement"""
    def __init__(self, name: str, color: Tuple[int, int, int], keys: dict):
        self.name = name
        self.color = color
        self.keys = keys
        self.selected_pos = [0, 0]  # Current selection position
        self.selected_piece = None  # Currently selected piece
        
class EnhancedKungFuChess:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        
        # Setup paths
        self.project_root = pathlib.Path(__file__).parent.parent
        self.pieces_dir = self.project_root / "pieces"
        
        # Board configuration
        self.cell_width = 80
        self.cell_height = 80
        self.board_width = 8
        self.board_height = 8
        
        # Screen setup
        self.screen_width = self.board_width * self.cell_width
        self.screen_height = self.board_height * self.cell_height + 100  # Extra space for info
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("🥋 Kung Fu Chess - No Turns!")
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        self.GREEN = (0, 255, 0)
        self.LIGHT_SQUARE = (240, 217, 181)
        self.DARK_SQUARE = (181, 136, 99)
        
        # Player setup
        self.player_a = PlayerSelection("Player A", self.RED, {
            'up': pygame.K_UP,
            'down': pygame.K_DOWN,
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT,
            'select': pygame.K_RETURN
        })
        
        self.player_b = PlayerSelection("Player B", self.BLUE, {
            'up': pygame.K_w,
            'down': pygame.K_s,
            'left': pygame.K_a,
            'right': pygame.K_d,
            'select': pygame.K_SPACE
        })
        
        # Initialize B's selection at a different position
        self.player_b.selected_pos = [7, 7]
        
        # Create game components
        self.board = self.create_board()
        self.piece_factory = PieceFactory(self.board, self.pieces_dir)
        self.pieces = self.create_initial_pieces()
        
        # Game timing
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

    def create_board(self) -> Board:
        """Create the game board."""
        try:
            board_img = Img()
            board_img.img = None  # We'll draw the board directly
            
            return Board(
                cell_H_pix=self.cell_height,
                cell_W_pix=self.cell_width,
                W_cells=self.board_width,
                H_cells=self.board_height,
                img=board_img
            )
        except Exception as e:
            print(f"❌ Error creating board: {e}")
            return None

    def create_initial_pieces(self) -> List[Piece]:
        """Create initial chess pieces."""
        pieces = []
        
        try:
            # Create a simple starting setup - just a few pieces for testing
            test_pieces = [
                ("PW", (6, 0), "♙"),  # White pawn
                ("PW", (6, 1), "♙"),  # White pawn
                ("PW", (6, 6), "♙"),  # White pawn
                ("PW", (6, 7), "♙"),  # White pawn
                ("PB", (1, 0), "♟"),  # Black pawn
                ("PB", (1, 1), "♟"),  # Black pawn
                ("PB", (1, 6), "♟"),  # Black pawn
                ("PB", (1, 7), "♟"),  # Black pawn
            ]
            
            for piece_type, pos, symbol in test_pieces:
                try:
                    # Create a simple piece representation
                    piece = {
                        'type': piece_type,
                        'pos': list(pos),
                        'symbol': symbol,
                        'state': 'idle',
                        'rest_until': 0,  # When the piece can move again
                        'color': 'white' if 'W' in piece_type else 'black'
                    }
                    pieces.append(piece)
                except Exception as e:
                    print(f"❌ Failed to create piece {piece_type}: {e}")
                    
        except Exception as e:
            print(f"❌ Error in piece creation: {e}")
        
        print(f"✅ Created {len(pieces)} pieces")
        return pieces

    def draw_board(self):
        """Draw the chess board."""
        for row in range(self.board_height):
            for col in range(self.board_width):
                x = col * self.cell_width
                y = row * self.cell_height
                
                # Checkerboard pattern
                if (row + col) % 2 == 0:
                    color = self.LIGHT_SQUARE
                else:
                    color = self.DARK_SQUARE
                
                pygame.draw.rect(self.screen, color, (x, y, self.cell_width, self.cell_height))

    def draw_selection_frames(self):
        """Draw selection frames for both players."""
        # Player A (Red frame)
        x_a = self.player_a.selected_pos[1] * self.cell_width
        y_a = self.player_a.selected_pos[0] * self.cell_height
        pygame.draw.rect(self.screen, self.player_a.color, 
                        (x_a, y_a, self.cell_width, self.cell_height), 4)
        
        # Player B (Blue frame)
        x_b = self.player_b.selected_pos[1] * self.cell_width
        y_b = self.player_b.selected_pos[0] * self.cell_height
        pygame.draw.rect(self.screen, self.player_b.color, 
                        (x_b, y_b, self.cell_width, self.cell_height), 4)

    def draw_pieces(self):
        """Draw all pieces on the board."""
        current_time = time.time()
        
        for piece in self.pieces:
            row, col = piece['pos']
            x = col * self.cell_width + self.cell_width // 2
            y = row * self.cell_height + self.cell_height // 2
            
            # Check if piece is in rest state
            in_rest = current_time < piece['rest_until']
            
            # Choose color based on piece color and state
            if piece['color'] == 'white':
                text_color = self.WHITE if not in_rest else (200, 200, 200)
            else:
                text_color = self.BLACK if not in_rest else (100, 100, 100)
            
            # Draw the piece symbol
            text_surface = self.font.render(piece['symbol'], True, text_color)
            text_rect = text_surface.get_rect(center=(x, y))
            self.screen.blit(text_surface, text_rect)
            
            # Draw rest indicator
            if in_rest:
                rest_time_left = piece['rest_until'] - current_time
                pygame.draw.circle(self.screen, self.RED, (x + 20, y - 20), 8)
                rest_text = self.small_font.render(f"{rest_time_left:.1f}", True, self.WHITE)
                rest_rect = rest_text.get_rect(center=(x + 20, y - 20))
                self.screen.blit(rest_text, rest_rect)

    def draw_info(self):
        """Draw game information."""
        y_offset = self.board_height * self.cell_height + 10
        
        # Player A info
        info_a = f"Player A (Red): {self.player_a.selected_pos} - Arrow Keys + Enter"
        text_a = self.small_font.render(info_a, True, self.RED)
        self.screen.blit(text_a, (10, y_offset))
        
        # Player B info
        info_b = f"Player B (Blue): {self.player_b.selected_pos} - WASD + Space"
        text_b = self.small_font.render(info_b, True, self.BLUE)
        self.screen.blit(text_b, (10, y_offset + 25))
        
        # Instructions
        instructions = "No turns! Move pieces anytime when not in rest state!"
        inst_text = self.small_font.render(instructions, True, self.BLACK)
        self.screen.blit(inst_text, (10, y_offset + 50))

    def get_piece_at(self, pos: Tuple[int, int]) -> Optional[dict]:
        """Get piece at the given position."""
        for piece in self.pieces:
            if piece['pos'] == list(pos):
                return piece
        return None

    def can_piece_move(self, piece: dict) -> bool:
        """Check if piece can move (not in rest state)."""
        return time.time() >= piece['rest_until']

    def move_piece(self, piece: dict, new_pos: Tuple[int, int]):
        """Move a piece to a new position."""
        if not self.can_piece_move(piece):
            print(f"❌ Piece at {piece['pos']} is still resting!")
            return False
        
        # Check if target square is empty or contains opponent piece
        target_piece = self.get_piece_at(new_pos)
        if target_piece and target_piece['color'] == piece['color']:
            print(f"❌ Cannot capture your own piece!")
            return False
        
        # Remove captured piece
        if target_piece:
            self.pieces.remove(target_piece)
            print(f"💥 {piece['symbol']} captures {target_piece['symbol']}!")
        
        # Move the piece
        old_pos = piece['pos'].copy()
        piece['pos'] = list(new_pos)
        
        # Set rest state (2 seconds for move)
        piece['rest_until'] = time.time() + 2.0
        piece['state'] = 'long_rest'
        
        print(f"✅ Moved {piece['symbol']} from {old_pos} to {new_pos}")
        return True

    def handle_player_input(self, player: PlayerSelection, key: int):
        """Handle input for a specific player."""
        # Movement
        if key == player.keys['up'] and player.selected_pos[0] > 0:
            player.selected_pos[0] -= 1
        elif key == player.keys['down'] and player.selected_pos[0] < self.board_height - 1:
            player.selected_pos[0] += 1
        elif key == player.keys['left'] and player.selected_pos[1] > 0:
            player.selected_pos[1] -= 1
        elif key == player.keys['right'] and player.selected_pos[1] < self.board_width - 1:
            player.selected_pos[1] += 1
        
        # Selection/Movement
        elif key == player.keys['select']:
            pos = tuple(player.selected_pos)
            piece = self.get_piece_at(pos)
            
            if player.selected_piece is None:
                # First click - select piece
                if piece and self.can_piece_move(piece):
                    player.selected_piece = piece
                    print(f"🎯 {player.name} selected {piece['symbol']} at {pos}")
                else:
                    if piece:
                        print(f"❌ {player.name}: Piece is resting!")
                    else:
                        print(f"❌ {player.name}: No piece at {pos}")
            else:
                # Second click - try to move
                if self.move_piece(player.selected_piece, pos):
                    player.selected_piece = None
                else:
                    # Invalid move, deselect
                    player.selected_piece = None

    def run(self):
        """Main game loop."""
        print("🥋 Starting Enhanced Kung Fu Chess!")
        print("🎮 Player A: Arrow keys + Enter")
        print("🎮 Player B: WASD + Space")
        print("🚪 Press ESC to quit")
        
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    else:
                        # Handle player inputs
                        if event.key in self.player_a.keys.values():
                            self.handle_player_input(self.player_a, event.key)
                        elif event.key in self.player_b.keys.values():
                            self.handle_player_input(self.player_b, event.key)
            
            # Clear screen
            self.screen.fill(self.WHITE)
            
            # Draw game elements
            self.draw_board()
            self.draw_selection_frames()
            self.draw_pieces()
            self.draw_info()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()

def main():
    """Main entry point."""
    print("🏗️ Setting up Enhanced Kung Fu Chess...")
    
    try:
        game = EnhancedKungFuChess()
        game.run()
    except Exception as e:
        print(f"❌ Failed to start game: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("👋 Thanks for playing Kung Fu Chess!")

if __name__ == "__main__":
    main()