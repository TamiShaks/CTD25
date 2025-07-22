import pygame
import sys
import time
import json
import os
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional


# Initialize Pygame
pygame.init()

# Constants
BOARD_SIZE = 8
SQUARE_SIZE = 80
WINDOW_WIDTH = BOARD_SIZE * SQUARE_SIZE
WINDOW_HEIGHT = BOARD_SIZE * SQUARE_SIZE + 100
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)
RED_FRAME = (255, 0, 0)
BLUE_FRAME = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
FROZEN_OVERLAY = (0, 150, 255, 128)  # Semi-transparent blue
SELECTED_OVERLAY = (255, 255, 0, 100)  # Semi-transparent yellow

class PieceType(Enum):
    PAWN = "P"
    ROOK = "R"
    KNIGHT = "N"
    BISHOP = "B"
    QUEEN = "Q"
    KING = "K"

class PieceColor(Enum):
    WHITE = "W"
    BLACK = "B"

class PieceState(Enum):
    IDLE = "idle"
    MOVE = "move"
    JUMP = "jump"
    SHORT_REST = "short_rest"  # 1 second after jump
    LONG_REST = "long_rest"    # 2 seconds after move

@dataclass
class SpriteConfig:
    frame_duration: float
    loop: bool

@dataclass
class Piece:
    piece_type: PieceType
    color: PieceColor
    row: int
    col: int
    state: PieceState = PieceState.IDLE
    rest_start_time: float = 0.0
    has_moved: bool = False  # For pawn double move and castling
    current_frame: int = 0
    frame_timer: float = 0.0

class SpriteManager:
    def __init__(self):
        self.sprites = {}
        self.configs = {}
        self.load_all_sprites()
    
    def get_piece_code(self, piece_type: PieceType, color: PieceColor) -> str:
        """Convert piece type and color to asset folder code"""
        return piece_type.value + color.value
    
    def load_all_sprites(self):
        """Load all sprites and configurations from the pieces folder"""
        pieces_dir = "pieces"
        if not os.path.exists(pieces_dir):
            print(f"Warning: {pieces_dir} folder not found. Using fallback rendering.")
            return
        
        piece_codes = ["PW", "PB", "RW", "RB", "NW", "NB", "BW", "BB", "QW", "QB", "KW", "KB"]
        states = ["idle", "move", "jump", "short_rest", "long_rest"]
        
        for piece_code in piece_codes:
            self.sprites[piece_code] = {}
            self.configs[piece_code] = {}
            
            for state in states:
                sprite_path = os.path.join(pieces_dir, piece_code, "states", state, "sprites")
                config_path = os.path.join(pieces_dir, piece_code, "states", state, "config.json")
                
                # Load config
                config = SpriteConfig(frame_duration=0.1, loop=True)  # Default config
                if os.path.exists(config_path):
                    try:
                        with open(config_path, 'r') as f:
                            config_data = json.load(f)
                            config = SpriteConfig(
                                frame_duration=config_data.get("frame_duration", 0.1),
                                loop=config_data.get("loop", True)
                            )
                    except Exception as e:
                        print(f"Error loading config for {piece_code}/{state}: {e}")
                
                self.configs[piece_code][state] = config
                
                # Load sprites
                sprites = []
                if os.path.exists(sprite_path):
                    for i in range(1, 6):  # Assuming 5 frames per animation
                        sprite_file = os.path.join(sprite_path, f"{i}.png")
                        if os.path.exists(sprite_file):
                            try:
                                sprite = pygame.image.load(sprite_file).convert_alpha()
                                # Scale sprite to fit square
                                sprite = pygame.transform.scale(sprite, (SQUARE_SIZE - 10, SQUARE_SIZE - 10))
                                sprites.append(sprite)
                            except Exception as e:
                                print(f"Error loading sprite {sprite_file}: {e}")
                
                self.sprites[piece_code][state] = sprites if sprites else []
    
    def get_sprite(self, piece: Piece) -> Optional[pygame.Surface]:
        """Get the current sprite for a piece"""
        piece_code = self.get_piece_code(piece.piece_type, piece.color)
        state = piece.state.value
        
        if piece_code not in self.sprites or state not in self.sprites[piece_code]:
            return None
        
        sprites = self.sprites[piece_code][state]
        if not sprites:
            return None
        
        # Return current frame
        return sprites[piece.current_frame % len(sprites)]
    
    def update_animation(self, piece: Piece, dt: float):
        """Update piece animation frame"""
        piece_code = self.get_piece_code(piece.piece_type, piece.color)
        state = piece.state.value
        
        if piece_code not in self.configs or state not in self.configs[piece_code]:
            return
        
        config = self.configs[piece_code][state]
        sprites = self.sprites.get(piece_code, {}).get(state, [])
        
        if not sprites:
            return
        
        piece.frame_timer += dt
        
        if piece.frame_timer >= config.frame_duration:
            piece.frame_timer = 0.0
            if config.loop:
                piece.current_frame = (piece.current_frame + 1) % len(sprites)
            else:
                piece.current_frame = min(piece.current_frame + 1, len(sprites) - 1)

class Player:
    def __init__(self, color: PieceColor, controls: Dict[str, int]):
        self.color = color
        self.controls = controls
        self.selected_row = 0 if color == PieceColor.WHITE else 7
        self.selected_col = 4
        self.frame_color = RED_FRAME if color == PieceColor.WHITE else BLUE_FRAME
        self.selected_piece_pos: Optional[Tuple[int, int]] = None  # Track selected piece

class KungFuChess:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Kung Fu Chess")
        self.clock = pygame.time.Clock()
        
        # Initialize sprite manager
        self.sprite_manager = SpriteManager()
        
        # Initialize board
        self.board: List[List[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]
        self.setup_board()
        
        # Players
        self.player1 = Player(PieceColor.WHITE, {
            'up': pygame.K_UP,
            'down': pygame.K_DOWN,
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT,
            'action': pygame.K_RETURN
        })
        
        self.player2 = Player(PieceColor.BLACK, {
            'up': pygame.K_w,
            'down': pygame.K_s,
            'left': pygame.K_a,
            'right': pygame.K_d,
            'action': pygame.K_SPACE
        })
        
        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.running = True
        self.keys_pressed = set()
        self.last_time = time.time()

    def setup_board(self):
        """Initialize the chess board with pieces"""
        # White pieces (bottom)
        piece_order = [PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN,
                      PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK]
        
        # White back rank
        for col in range(8):
            self.board[7][col] = Piece(piece_order[col], PieceColor.WHITE, 7, col)
        
        # White pawns
        for col in range(8):
            self.board[6][col] = Piece(PieceType.PAWN, PieceColor.WHITE, 6, col)
        
        # Black back rank
        for col in range(8):
            self.board[0][col] = Piece(piece_order[col], PieceColor.BLACK, 0, col)
        
        # Black pawns
        for col in range(8):
            self.board[1][col] = Piece(PieceType.PAWN, PieceColor.BLACK, 1, col)

    def get_piece_symbol(self, piece: Piece) -> str:
        """Get unicode symbol for piece (fallback when sprites not available)"""
        symbols = {
            (PieceType.KING, PieceColor.WHITE): "♔",
            (PieceType.QUEEN, PieceColor.WHITE): "♕",
            (PieceType.ROOK, PieceColor.WHITE): "♖",
            (PieceType.BISHOP, PieceColor.WHITE): "♗",
            (PieceType.KNIGHT, PieceColor.WHITE): "♘",
            (PieceType.PAWN, PieceColor.WHITE): "♙",
            (PieceType.KING, PieceColor.BLACK): "♚",
            (PieceType.QUEEN, PieceColor.BLACK): "♛",
            (PieceType.ROOK, PieceColor.BLACK): "♜",
            (PieceType.BISHOP, PieceColor.BLACK): "♝",
            (PieceType.KNIGHT, PieceColor.BLACK): "♞",
            (PieceType.PAWN, PieceColor.BLACK): "♟",
        }
        return symbols.get((piece.piece_type, piece.color), "?")

    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if position is within board bounds"""
        return 0 <= row < 8 and 0 <= col < 8

    def get_legal_moves(self, piece: Piece) -> List[Tuple[int, int]]:
        """Get all legal moves for a piece"""
        moves = []
        row, col = piece.row, piece.col
        
        if piece.piece_type == PieceType.PAWN:
            direction = -1 if piece.color == PieceColor.WHITE else 1
            
            # Forward move
            new_row = row + direction
            if self.is_valid_position(new_row, col) and self.board[new_row][col] is None:
                moves.append((new_row, col))
                
                # Double move from starting position
                if not piece.has_moved:
                    new_row2 = row + 2 * direction
                    if self.is_valid_position(new_row2, col) and self.board[new_row2][col] is None:
                        moves.append((new_row2, col))
            
            # Captures
            for dc in [-1, 1]:
                new_row, new_col = row + direction, col + dc
                if self.is_valid_position(new_row, new_col):
                    target = self.board[new_row][new_col]
                    if target and target.color != piece.color:
                        moves.append((new_row, new_col))
        
        elif piece.piece_type == PieceType.ROOK:
            # Horizontal and vertical moves
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for dr, dc in directions:
                for i in range(1, 8):
                    new_row, new_col = row + dr * i, col + dc * i
                    if not self.is_valid_position(new_row, new_col):
                        break
                    target = self.board[new_row][new_col]
                    if target is None:
                        moves.append((new_row, new_col))
                    elif target.color != piece.color:
                        moves.append((new_row, new_col))
                        break
                    else:
                        break
        
        elif piece.piece_type == PieceType.BISHOP:
            # Diagonal moves
            directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dr, dc in directions:
                for i in range(1, 8):
                    new_row, new_col = row + dr * i, col + dc * i
                    if not self.is_valid_position(new_row, new_col):
                        break
                    target = self.board[new_row][new_col]
                    if target is None:
                        moves.append((new_row, new_col))
                    elif target.color != piece.color:
                        moves.append((new_row, new_col))
                        break
                    else:
                        break
        
        elif piece.piece_type == PieceType.QUEEN:
            # Combination of rook and bishop
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dr, dc in directions:
                for i in range(1, 8):
                    new_row, new_col = row + dr * i, col + dc * i
                    if not self.is_valid_position(new_row, new_col):
                        break
                    target = self.board[new_row][new_col]
                    if target is None:
                        moves.append((new_row, new_col))
                    elif target.color != piece.color:
                        moves.append((new_row, new_col))
                        break
                    else:
                        break
        
        elif piece.piece_type == PieceType.KNIGHT:
            # L-shaped moves
            knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
            for dr, dc in knight_moves:
                new_row, new_col = row + dr, col + dc
                if self.is_valid_position(new_row, new_col):
                    target = self.board[new_row][new_col]
                    if target is None or target.color != piece.color:
                        moves.append((new_row, new_col))
        
        elif piece.piece_type == PieceType.KING:
            # One square in any direction
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                if self.is_valid_position(new_row, new_col):
                    target = self.board[new_row][new_col]
                    if target is None or target.color != piece.color:
                        moves.append((new_row, new_col))
        
        return moves

    def update_piece_states(self, dt: float):
        """Update piece states and animations based on time"""
        current_time = time.time()
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    # Update animation
                    self.sprite_manager.update_animation(piece, dt)
                    
                    # Update state transitions
                    if piece.state in [PieceState.SHORT_REST, PieceState.LONG_REST]:
                        rest_duration = 1.0 if piece.state == PieceState.SHORT_REST else 2.0
                        if current_time - piece.rest_start_time >= rest_duration:
                            piece.state = PieceState.IDLE
                            piece.current_frame = 0  # Reset animation

    def can_piece_act(self, piece: Piece) -> bool:
        print(f"DEBUG: Piece at ({piece.row}, {piece.col}) state: {piece.state}")
        return piece.state == PieceState.IDLE

    def handle_player_action(self, player: Player):
        selected_piece = self.board[player.selected_row][player.selected_col]

        if selected_piece and selected_piece.color == player.color:
            if player.selected_piece_pos == (player.selected_row, player.selected_col):
                self.jump_piece(player.selected_row, player.selected_col)
                player.selected_piece_pos = None
            else:
                player.selected_piece_pos = (player.selected_row, player.selected_col)
                print(f"DEBUG: Selected piece at {player.selected_piece_pos}")
        else:
            if player.selected_piece_pos:
                from_row, from_col = player.selected_piece_pos
                piece = self.board[from_row][from_col]

                print(f"DEBUG: Attempting move from ({from_row},{from_col}) to ({player.selected_row},{player.selected_col})")
                print(f"DEBUG: Piece = {piece}, Can act? {self.can_piece_act(piece)}")
                print(f"DEBUG: Legal moves = {self.get_legal_moves(piece)}")

                if piece and piece.color == player.color and self.can_piece_act(piece):
                    legal_moves = self.get_legal_moves(piece)
                    if (player.selected_row, player.selected_col) in legal_moves:
                        if self.move_piece(from_row, from_col, player.selected_row, player.selected_col):
                            print("DEBUG: Move successful!")
                            player.selected_piece_pos = None
                            return

                print("DEBUG: Move failed. Deselecting.")
                player.selected_piece_pos = None

            else:
                for row in range(8):
                    for col in range(8):
                        piece = self.board[row][col]
                        if piece and piece.color == player.color and self.can_piece_act(piece):
                            legal_moves = self.get_legal_moves(piece)
                            if (player.selected_row, player.selected_col) in legal_moves:
                                if self.move_piece(row, col, player.selected_row, player.selected_col):
                                    print("DEBUG: Fallback move success")
                                    return

    def move_piece(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Move a piece from one position to another"""
        piece = self.board[from_row][from_col]
        if not piece or not self.can_piece_act(piece):
            return False
        
        legal_moves = self.get_legal_moves(piece)
        if (to_row, to_col) not in legal_moves:
            return False
        
        # Perform the move
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        
        # Update piece position and state
        piece.row = to_row
        piece.col = to_col
        piece.has_moved = True
        piece.state = PieceState.LONG_REST
        piece.rest_start_time = time.time()
        piece.current_frame = 0  # Reset animation
        
        return True

    def jump_piece(self, row: int, col: int) -> bool:
        """Make a piece jump (no movement, just rest)"""
        piece = self.board[row][col]
        if not piece or not self.can_piece_act(piece):
            return False
        
        piece.state = PieceState.SHORT_REST
        piece.rest_start_time = time.time()
        piece.current_frame = 0  # Reset animation
        return True

    def handle_input(self):
        """Handle keyboard input for both players"""
        keys = pygame.key.get_pressed()
        
        # Player 1 (White) controls
        if keys[self.player1.controls['up']] and pygame.K_UP not in self.keys_pressed:
            self.player1.selected_row = max(0, self.player1.selected_row - 1)
            self.keys_pressed.add(pygame.K_UP)
        if keys[self.player1.controls['down']] and pygame.K_DOWN not in self.keys_pressed:
            self.player1.selected_row = min(7, self.player1.selected_row + 1)
            self.keys_pressed.add(pygame.K_DOWN)
        if keys[self.player1.controls['left']] and pygame.K_LEFT not in self.keys_pressed:
            self.player1.selected_col = max(0, self.player1.selected_col - 1)
            self.keys_pressed.add(pygame.K_LEFT)
        if keys[self.player1.controls['right']] and pygame.K_RIGHT not in self.keys_pressed:
            self.player1.selected_col = min(7, self.player1.selected_col + 1)
            self.keys_pressed.add(pygame.K_RIGHT)
        if keys[self.player1.controls['action']] and pygame.K_RETURN not in self.keys_pressed:
            self.handle_player_action(self.player1)
            self.keys_pressed.add(pygame.K_RETURN)
        
        # Player 2 (Black) controls
        if keys[self.player2.controls['up']] and pygame.K_w not in self.keys_pressed:
            self.player2.selected_row = max(0, self.player2.selected_row - 1)
            self.keys_pressed.add(pygame.K_w)
        if keys[self.player2.controls['down']] and pygame.K_s not in self.keys_pressed:
            self.player2.selected_row = min(7, self.player2.selected_row + 1)
            self.keys_pressed.add(pygame.K_s)
        if keys[self.player2.controls['left']] and pygame.K_a not in self.keys_pressed:
            self.player2.selected_col = max(0, self.player2.selected_col - 1)
            self.keys_pressed.add(pygame.K_a)
        if keys[self.player2.controls['right']] and pygame.K_d not in self.keys_pressed:
            self.player2.selected_col = min(7, self.player2.selected_col + 1)
            self.keys_pressed.add(pygame.K_d)
        if keys[self.player2.controls['action']] and pygame.K_SPACE not in self.keys_pressed:
            self.handle_player_action(self.player2)
            self.keys_pressed.add(pygame.K_SPACE)
        
        # Clear keys that are no longer pressed
        for key in list(self.keys_pressed):
            if not keys[key]:
                self.keys_pressed.discard(key)

    # def handle_player_action(self, player: Player):
    #     """Handle when a player presses their action key"""
    #     selected_piece = self.board[player.selected_row][player.selected_col]
        
    #     # If clicking on own piece
    #     if selected_piece and selected_piece.color == player.color:
    #         if player.selected_piece_pos == (player.selected_row, player.selected_col):
    #             # Double-click on same piece = jump
    #             self.jump_piece(player.selected_row, player.selected_col)
    #             player.selected_piece_pos = None
    #         else:
    #             # Select this piece
    #             player.selected_piece_pos = (player.selected_row, player.selected_col)
    #     else:
    #         # If we have a piece selected, try to move it here
    #         if player.selected_piece_pos:
    #             from_row, from_col = player.selected_piece_pos
    #             piece = self.board[from_row][from_col]
                
    #             if (piece and piece.color == player.color and 
    #                 self.can_piece_act(piece)):
    #                 legal_moves = self.get_legal_moves(piece)
    #                 if (player.selected_row, player.selected_col) in legal_moves:
    #                     if self.move_piece(from_row, from_col, player.selected_row, player.selected_col):
    #                         player.selected_piece_pos = None
    #                         return
                
    #             # If move failed, deselect
    #             player.selected_piece_pos = None
    #         else:
    #             # No piece selected, try to find a piece that can move here
    #             # This is the fallback behavior for the old system
    #             for row in range(8):
    #                 for col in range(8):
    #                     piece = self.board[row][col]
    #                     if (piece and piece.color == player.color and 
    #                         self.can_piece_act(piece)):
    #                         legal_moves = self.get_legal_moves(piece)
    #                         if (player.selected_row, player.selected_col) in legal_moves:
    #                             if self.move_piece(row, col, player.selected_row, player.selected_col):
    #                                 return

    def draw_board(self):
        """Draw the chess board"""
        for row in range(8):
            for col in range(8):
                color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
                rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(self.screen, color, rect)

    def draw_pieces(self):
        """Draw all pieces on the board"""
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    x = col * SQUARE_SIZE
                    y = row * SQUARE_SIZE
                    
                    # Draw selected piece highlight
                    if ((self.player1.selected_piece_pos == (row, col)) or 
                        (self.player2.selected_piece_pos == (row, col))):
                        overlay = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                        overlay.fill(SELECTED_OVERLAY)
                        self.screen.blit(overlay, (x, y))
                    
                    # Try to get sprite first
                    sprite = self.sprite_manager.get_sprite(piece)
                    
                    if sprite:
                        # Draw sprite
                        sprite_rect = sprite.get_rect()
                        sprite_rect.center = (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2)
                        self.screen.blit(sprite, sprite_rect)
                    else:
                        # Fallback to unicode symbol
                        symbol = self.get_piece_symbol(piece)
                        text_color = BLACK
                        if piece.state == PieceState.SHORT_REST:
                            text_color = YELLOW
                        elif piece.state == PieceState.LONG_REST:
                            text_color = (128, 128, 128)  # Gray
                        
                        text = self.font.render(symbol, True, text_color)
                        text_rect = text.get_rect()
                        text_rect.center = (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2)
                        self.screen.blit(text, text_rect)
                    
                    # Draw frozen overlay for pieces that can't act
                    if not self.can_piece_act(piece):
                        overlay = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                        overlay.fill(FROZEN_OVERLAY)
                        
                        # Add ice/frozen effect pattern
                        for i in range(0, SQUARE_SIZE, 10):
                            pygame.draw.line(overlay, (200, 230, 255, 150), 
                                           (i, 0), (i, SQUARE_SIZE), 2)
                        for i in range(0, SQUARE_SIZE, 10):
                            pygame.draw.line(overlay, (200, 230, 255, 150), 
                                           (0, i), (SQUARE_SIZE, i), 2)
                        
                        self.screen.blit(overlay, (x, y))

    def draw_legal_moves(self, player: Player):
        """Draw legal moves for selected piece"""
        if player.selected_piece_pos:
            row, col = player.selected_piece_pos
            piece = self.board[row][col]
            if piece and self.can_piece_act(piece):
                legal_moves = self.get_legal_moves(piece)
                for move_row, move_col in legal_moves:
                    x = move_col * SQUARE_SIZE
                    y = move_row * SQUARE_SIZE
                    
                    # Draw a small circle to indicate legal move
                    center = (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2)
                    pygame.draw.circle(self.screen, GREEN, center, 8)
                    pygame.draw.circle(self.screen, WHITE, center, 6)

    def draw_selection_frames(self):
        """Draw selection frames for both players"""
        # Player 1 (Red frame)
        rect1 = pygame.Rect(self.player1.selected_col * SQUARE_SIZE,
                           self.player1.selected_row * SQUARE_SIZE,
                           SQUARE_SIZE, SQUARE_SIZE)
        pygame.draw.rect(self.screen, self.player1.frame_color, rect1, 3)
        
        # Player 2 (Blue frame)
        rect2 = pygame.Rect(self.player2.selected_col * SQUARE_SIZE,
                           self.player2.selected_row * SQUARE_SIZE,
                           SQUARE_SIZE, SQUARE_SIZE)
        pygame.draw.rect(self.screen, self.player2.frame_color, rect2, 3)

    def draw_ui(self):
        """Draw user interface elements"""
        y_offset = BOARD_SIZE * SQUARE_SIZE + 10
        
        # Instructions
        instructions = [
            "Player 1 (Red): Arrow Keys + Enter | Player 2 (Blue): WASD + Space",
            "Select piece first, then target square to move | Double-click piece to jump",
            "Yellow highlight = selected piece | Green dots = legal moves | Frozen overlay = resting"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, BLACK)
            self.screen.blit(text, (10, y_offset + i * 20))

    def draw(self):
        """Main drawing function"""
        self.screen.fill(WHITE)
        self.draw_board()
        self.draw_pieces()
        self.draw_legal_moves(self.player1)
        self.draw_legal_moves(self.player2)
        self.draw_selection_frames()
        self.draw_ui()
        pygame.display.flip()

    def run(self):
        """Main game loop"""
        while self.running:
            current_time = time.time()
            dt = current_time - self.last_time
            self.last_time = current_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            
            self.handle_input()
            self.update_piece_states(dt)
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = KungFuChess()
    game.run()