import inspect
import pathlib
import queue, threading, time, cv2, math
from typing import List, Dict, Tuple, Optional
from Board import Board
from Command import Command
from Piece import Piece
from img import Img

class InvalidBoard(Exception): 
    pass

class Game:
    def __init__(self, pieces: List[Piece], board: Board):
        """Initialize the game with pieces, board, and optional event bus."""
        self.pieces = pieces
        self.board = board
        self.start_time = time.time()
        self.user_input_queue = queue.Queue()
        
        # Player selections - track selected cell for each player
        self.player_a_selection = (0, 0)  # Player A (arrow keys) - red frame
        self.player_b_selection = (0, 1)  # Player B (WASD) - blue frame
        
        # Find pieces by player (assuming piece IDs indicate ownership)
        self.player_a_pieces = [p for p in pieces if 'A' in p.piece_id or 'W' in p.piece_id]
        self.player_b_pieces = [p for p in pieces if 'B' in p.piece_id or 'B' in p.piece_id]
        
    def game_time_ms(self) -> int:
        """Return the current game time in milliseconds."""
        return int((time.time() - self.start_time) * 1000)

    def clone_board(self) -> Board:
        """Return a brand-new Board wrapping a copy of the background pixels."""
        return self.board.clone()

    def start_user_input_thread(self):
        """Start the user input thread for mouse handling."""
        def input_worker():
            while True:
                key = cv2.waitKey(1) & 0xFF
                if key == 255:  # No key pressed
                    continue
                    
                now = self.game_time_ms()
                cmd = None
                
                # Player A controls (Arrow keys)
                if key == 82:  # Up arrow
                    new_pos = (max(0, self.player_a_selection[0] - 1), self.player_a_selection[1])
                    self.player_a_selection = new_pos
                elif key == 84:  # Down arrow  
                    new_pos = (min(self.board.H_cells - 1, self.player_a_selection[0] + 1), self.player_a_selection[1])
                    self.player_a_selection = new_pos
                elif key == 81:  # Left arrow
                    new_pos = (self.player_a_selection[0], max(0, self.player_a_selection[1] - 1))
                    self.player_a_selection = new_pos
                elif key == 83:  # Right arrow
                    new_pos = (self.player_a_selection[0], min(self.board.W_cells - 1, self.player_a_selection[1] + 1))
                    self.player_a_selection = new_pos
                elif key == 13:  # Enter - Player A move
                    cmd = Command(now, "player_a", "Move", [self.player_a_selection])
                    
                # Player B controls (WASD)
                elif key == ord('w') or key == ord('W'):
                    new_pos = (max(0, self.player_b_selection[0] - 1), self.player_b_selection[1])
                    self.player_b_selection = new_pos
                elif key == ord('s') or key == ord('S'):
                    new_pos = (min(self.board.H_cells - 1, self.player_b_selection[0] + 1), self.player_b_selection[1])
                    self.player_b_selection = new_pos
                elif key == ord('a') or key == ord('A'):
                    new_pos = (self.player_b_selection[0], max(0, self.player_b_selection[1] - 1))
                    self.player_b_selection = new_pos
                elif key == ord('d') or key == ord('D'):
                    new_pos = (self.player_b_selection[0], min(self.board.W_cells - 1, self.player_b_selection[1] + 1))
                    self.player_b_selection = new_pos
                elif key == ord(' '):  # Space - Player B move
                    cmd = Command(now, "player_b", "Move", [self.player_b_selection])
                elif key == 27:  # Escape
                    break
                    
                if cmd:
                    self.user_input_queue.put(cmd)
                    
        thread = threading.Thread(target=input_worker, daemon=True)
        thread.start()

    def run(self):
        """Main game loop."""
        self.start_user_input_thread()

        start_ms = self.game_time_ms()
        for p in self.pieces:
            p.reset(start_ms)

        # Main loop
        while not self._is_win():
            now = self.game_time_ms()

            # (1) Update physics & animations
            for p in self.pieces:
                p.update(now)

            # (2) Handle queued Commands from input thread
            while not self.user_input_queue.empty():
                cmd: Command = self.user_input_queue.get()
                self._process_input(cmd)

            # (3) Draw current position
            self._draw()
            if not self._show():
                break

            # (4) Detect captures
            self._resolve_collisions()

        self._announce_win()
        cv2.destroyAllWindows()

    def _process_input(self, cmd: Command):
        """Process player input commands."""
        if cmd.type == "Move":
            target_cell = cmd.params[0]
            
            # Find the piece at the selected position
            selected_piece = None
            if cmd.piece_id == "player_a":
                # Find Player A piece at their selection
                current_pos = self.player_a_selection
                for piece in self.player_a_pieces:
                    piece_pos = self._get_piece_cell_position(piece)
                    if piece_pos == current_pos:
                        selected_piece = piece
                        break
            elif cmd.piece_id == "player_b":
                # Find Player B piece at their selection  
                current_pos = self.player_b_selection
                for piece in self.player_b_pieces:
                    piece_pos = self._get_piece_cell_position(piece)
                    if piece_pos == current_pos:
                        selected_piece = piece
                        break
            
            if selected_piece:
                # Validate and execute move
                if self._is_valid_move(selected_piece, target_cell):
                    selected_piece.on_command(cmd, self.game_time_ms())

    def _get_piece_cell_position(self, piece: Piece) -> Tuple[int, int]:
        """Get the current cell position of a piece."""
        # This would depend on your Physics implementation
        # For now, return a placeholder
        return (0, 0)
        
    def _is_valid_move(self, piece: Piece, target_cell: Tuple[int, int]) -> bool:
        """Check if a move is valid for the given piece."""
        # Check if piece is in idle state (not in rest)
        if not piece.current_state.can_transition(self.game_time_ms()):
            return False
            
        # Check if move is legal according to piece's move set
        current_pos = self._get_piece_cell_position(piece)
        relative_move = (target_cell[0] - current_pos[0], target_cell[1] - current_pos[1])
        
        # This would check against the piece's Moves object
        valid_moves = piece.current_state.moves.get_moves(current_pos[0], current_pos[1])
        return target_cell in valid_moves

    def _draw(self):
        """Draw the current game state."""
        # Clone board for drawing
        display_board = self.clone_board()
        
        # Draw all pieces
        now = self.game_time_ms()
        for piece in self.pieces:
            piece.draw_on_board(display_board, now)
            
        # Draw selection frames
        self._draw_selection_frame(display_board, self.player_a_selection, (0, 0, 255))  # Red for Player A
        self._draw_selection_frame(display_board, self.player_b_selection, (255, 0, 0))  # Blue for Player B
        
        self.current_display = display_board

    def _draw_selection_frame(self, board: Board, cell_pos: Tuple[int, int], color: Tuple[int, int, int]):
        """Draw a selection frame around a cell."""
        row, col = cell_pos
        x = col * board.cell_W_pix
        y = row * board.cell_H_pix
        
        # Draw frame rectangle
        cv2.rectangle(board.img.img, 
                     (x, y), 
                     (x + board.cell_W_pix, y + board.cell_H_pix), 
                     color, 3)

    def _show(self) -> bool:
        """Show the current frame and handle window events."""
        if hasattr(self, 'current_display'):
            cv2.imshow("Kung Fu Chess", self.current_display.img.img)
            return cv2.waitKey(1) & 0xFF != 27  # Return False if ESC pressed
        return True

    def _resolve_collisions(self):
        """Resolve piece collisions and captures."""
        # Implementation for capture logic
        pass

    def _is_win(self) -> bool:
        """Check if the game has ended."""
        # Check for win conditions (e.g., king captured)
        return False

    def _announce_win(self):
        """Announce the winner."""
        print("Game Over!")

        """Announce the winner."""
        if len(self.pieces) == 0:
            print("Game ended - No pieces remaining!")
        elif len(self.pieces) == 1:
            winner_type = self.pieces[0].piece_id.split('_')[0]
            print(f"Game ended - {winner_type} wins!")
        else:
            remaining_types = set(piece.piece_id.split('_')[0] for piece in self.pieces)
            if len(remaining_types) == 1:
                winner_type = list(remaining_types)[0]
                print(f"Game ended - {winner_type} wins!")
            else:
                print("Game ended!")