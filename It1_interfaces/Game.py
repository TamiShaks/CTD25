# import inspect
# import pathlib
# import queue, threading, time, cv2, math
# from typing import List, Dict, Tuple, Optional
# from Board   import Board
# from Bus.bus import EventBus, Event
# from Command import Command
# from Piece   import Piece
# from img     import Img


# class InvalidBoard(Exception): ...
# # ────────────────────────────────────────────────────────────────────
# class Game:
#     def __init__(self, pieces: List[Piece], board: Board):
#         """Initialize the game with pieces, board, and optional event bus."""
#         pass

#     # ─── helpers ─────────────────────────────────────────────────────────────
#     def game_time_ms(self) -> int:
#         """Return the current game time in milliseconds."""
#         pass

#     def clone_board(self) -> Board:
#         """
#         Return a **brand-new** Board wrapping a copy of the background pixels
#         so we can paint sprites without touching the pristine board.
#         """
#         pass

#     def start_user_input_thread(self):
#         """Start the user input thread for mouse handling."""
#         pass

#     # ─── main public entrypoint ──────────────────────────────────────────────
#     def run(self):
#         """Main game loop."""
#         self.start_user_input_thread() # QWe2e5

#         start_ms = self.game_time_ms()
#         for p in self.pieces:
#             p.reset(start_ms)

#         # ─────── main loop ──────────────────────────────────────────────────
#         while not self._is_win():
#             now = self.game_time_ms() # monotonic time ! not computer time.

#             # (1) update physics & animations
#             for p in self.pieces:
#                 p.update(now)

#             # (2) handle queued Commands from mouse thread
#             while not self.user_input_queue.empty(): # QWe2e5
#                 cmd: Command = self.user_input_queue.get()
#                 self._process_input(cmd)

#             # (3) draw current position
#             self._draw()
#             if not self._show():           # returns False if user closed window
#                 break

#             # (4) detect captures
#             self._resolve_collisions()

#         self._announce_win()
#         cv2.destroyAllWindows()

#     # ─── drawing helpers ────────────────────────────────────────────────────
#     def _draw(self):
#         """Draw the current game state."""
#         pass

#     def _show(self) -> bool:
#         """Show the current frame and handle window events."""
#         pass

#     # ─── capture resolution ────────────────────────────────────────────────
#     def _resolve_collisions(self):
#         """Resolve piece collisions and captures."""
#         pass

#     # ─── board validation & win detection ───────────────────────────────────
#     def _is_win(self) -> bool:
#         """Check if the game has ended."""
#         pass

#     def _announce_win(self):
#         """Announce the winner."""
#         pass


import inspect
import pathlib
import queue, threading, time, cv2, math
from typing import List, Dict, Tuple, Optional
from Board   import Board
from Bus.bus import EventBus, Event
from Command import Command
from Piece   import Piece
from img     import Img

class InvalidBoard(Exception): 
    pass

class Game:
    def __init__(self, pieces: List[Piece], board: Board):
        """Initialize the game with pieces, board, and optional event bus."""
        self.pieces = pieces
        self.board = board
        self.event_bus = EventBus()
        self.user_input_queue = queue.Queue()
        self.start_time = None
        
        # Game state
        self.running = True
        self.winner = None

    def game_time_ms(self) -> int:
        """Return the current game time in milliseconds."""
        if self.start_time is None:
            self.start_time = time.time() * 1000
        return int(time.time() * 1000 - self.start_time)

    def clone_board(self) -> Board:
        """Return a brand-new Board wrapping a copy of the background pixels."""
        return self.board.clone()

    def start_user_input_thread(self):
        """Start the user input thread for mouse handling."""
        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                # Convert pixel to cell coordinates
                row, col = self.board.pixel_to_cell(x, y)
                
                if self.board.is_valid_cell(row, col):
                    # Find piece at this location
                    clicked_piece = self._find_piece_at_cell(row, col)
                    
                    if clicked_piece:
                        # Create move command (simple: move one cell right as example)
                        target_cell = (row, min(col + 1, self.board.W_cells - 1))
                        
                        cmd = Command(
                            timestamp=self.game_time_ms(),
                            piece_id=clicked_piece.piece_id,
                            type="Move",
                            params=[(row, col), target_cell]
                        )
                        
                        self.user_input_queue.put(cmd)
        
        cv2.namedWindow("Kung Fu Chess")
        cv2.setMouseCallback("Kung Fu Chess", mouse_callback)

    def _find_piece_at_cell(self, row: int, col: int) -> Optional[Piece]:
        """Find a piece at the given cell coordinates."""
        for piece in self.pieces:
            piece_row, piece_col = piece.current_state.physics.current_cell
            if piece_row == row and piece_col == col:
                return piece
        return None

    def run(self):
        """Main game loop."""
        self.start_user_input_thread()

        start_ms = self.game_time_ms()
        for p in self.pieces:
            p.reset(start_ms)

        # Main loop
        while not self._is_win() and self.running:
            now = self.game_time_ms()

            # (1) Update physics & animations
            for p in self.pieces:
                p.update(now)

            # (2) Handle queued Commands from mouse thread
            while not self.user_input_queue.empty():
                cmd: Command = self.user_input_queue.get()
                self._process_input(cmd)

            # (3) Draw current position
            self._draw()
            if not self._show():
                break

            # (4) Detect captures
            self._resolve_collisions()

            # Small delay to prevent excessive CPU usage
            time.sleep(0.016)  # ~60 FPS

        self._announce_win()
        cv2.destroyAllWindows()

    def _process_input(self, cmd: Command):
        """Process a user input command."""
        for piece in self.pieces:
            piece.on_command(cmd, cmd.timestamp)

    def _draw(self):
        """Draw the current game state."""
        # Start with a fresh board
        current_board = self.clone_board()
        
        # Draw all pieces
        for piece in self.pieces:
            piece.draw_on_board(current_board, self.game_time_ms())
        
        # Store the rendered board
        self.rendered_board = current_board

    def _show(self) -> bool:
        """Show the current frame and handle window events."""
        if hasattr(self, 'rendered_board') and self.rendered_board.img.img is not None:
            cv2.imshow("Kung Fu Chess", self.rendered_board.img.img)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 'q' or ESC
                return False
                
            # Check if window was closed
            if cv2.getWindowProperty("Kung Fu Chess", cv2.WND_PROP_VISIBLE) < 1:
                return False
                
            return True
        return False

    def _resolve_collisions(self):
        """Resolve piece collisions and captures."""
        pieces_to_remove = []
        
        for i, piece1 in enumerate(self.pieces):
            for j, piece2 in enumerate(self.pieces):
                if i >= j:
                    continue
                    
                # Check if pieces are in the same cell
                pos1 = piece1.current_state.physics.current_cell
                pos2 = piece2.current_state.physics.current_cell
                
                if pos1 == pos2:
                    # Collision detected!
                    if piece1.current_state.physics.can_capture() and piece2.current_state.physics.can_be_captured():
                        pieces_to_remove.append(piece2)
                    elif piece2.current_state.physics.can_capture() and piece1.current_state.physics.can_be_captured():
                        pieces_to_remove.append(piece1)
        
        # Remove captured pieces
        for piece in pieces_to_remove:
            if piece in self.pieces:
                self.pieces.remove(piece)

    def _is_win(self) -> bool:
        """Check if the game has ended."""
        # Simple win condition: only one piece type remains
        if len(self.pieces) <= 1:
            return True
            
        # Check if all remaining pieces are of the same type
        piece_types = set()
        for piece in self.pieces:
            piece_type = piece.piece_id.split('_')[0]  # Extract type from ID
            piece_types.add(piece_type)
            
        return len(piece_types) <= 1

    def _announce_win(self):
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