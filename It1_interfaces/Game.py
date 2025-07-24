import inspect
import pathlib
import queue, threading, time, cv2, math
from typing import List, Dict, Tuple, Optional
from It1_interfaces.Board import Board
from It1_interfaces.Command import Command
from It1_interfaces.Piece import Piece
from It1_interfaces.img import Img


class InvalidBoard(Exception): ...
# ────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self, pieces: List[Piece], board: Board, event_bus=None):
        """Initialize the game with pieces, board, and optional event bus."""
        self.pieces = {p.piece_id: p for p in pieces}
        self.board = board
        self.start_time = time.time()
        self.user_input_queue = queue.Queue()
        self.event_bus = event_bus
        self.selection = {
            'A': {'pos': [0, 0], 'selected': None, 'color': (255, 0, 0)},
            'B': {'pos': [7, 7], 'selected': None, 'color': (0, 0, 255)}
        }

    # ─── helpers ─────────────────────────────────────────────────────────────
    def game_time_ms(self) -> int:
        """Return the current game time in milliseconds."""
        return int((time.time() - self.start_time) * 1000)

    def clone_board(self) -> Board:
        """
        Return a **brand-new** Board wrapping a copy of the background pixels
        so we can paint sprites without touching the pristine board.
        """
        return self.board.clone()

    def _draw(self):
        """Draw the current game state."""
        board_img = self.clone_board().img
        for piece in self.pieces.values():
            piece.draw_on_board(board_img, self.game_time_ms())
        # Draw selection rectangles
        for player in ['A', 'B']:
            pos = self.selection[player]['pos']
            color = self.selection[player]['color']
            import cv2
            x = pos[1] * self.board.cell_W_pix
            y = pos[0] * self.board.cell_H_pix
            cv2.rectangle(board_img.img, (x, y), (x + self.board.cell_W_pix, y + self.board.cell_H_pix), color, 3)
            selected_piece = self.selection[player]['selected']
            if selected_piece:
                # Draw rectangle around selected piece
                p_pos = selected_piece.current_state.physics.current_cell
                sx = p_pos[1] * self.board.cell_W_pix
                sy = p_pos[0] * self.board.cell_H_pix
                cv2.rectangle(board_img.img, (sx, sy), (sx + self.board.cell_W_pix, sy + self.board.cell_H_pix), color, 5)
        self.current_display = board_img

    def start_user_input_thread(self):
        """Start the user input thread for keyboard handling."""
        import pygame
        pygame.init()
        clock = pygame.time.Clock()
        self._should_quit = False

        def input_worker():
            while not self._should_quit:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self._should_quit = True
                    elif event.type == pygame.KEYDOWN:
                        # Player A controls
                        if event.key == pygame.K_UP:
                            self._move_selection('A', 'up')
                        elif event.key == pygame.K_DOWN:
                            self._move_selection('A', 'down')
                        elif event.key == pygame.K_LEFT:
                            self._move_selection('A', 'left')
                        elif event.key == pygame.K_RIGHT:
                            self._move_selection('A', 'right')
                        elif event.key == pygame.K_RETURN:
                            self._select_piece('A')
                        # Player B controls
                        elif event.key == pygame.K_w:
                            self._move_selection('B', 'up')
                        elif event.key == pygame.K_s:
                            self._move_selection('B', 'down')
                        elif event.key == pygame.K_a:
                            self._move_selection('B', 'left')
                        elif event.key == pygame.K_d:
                            self._move_selection('B', 'right')
                        elif event.key == pygame.K_SPACE:
                            self._select_piece('B')
                clock.tick(30)
        import threading
        thread = threading.Thread(target=input_worker, daemon=True)
        thread.start()

    # ─── main public entrypoint ──────────────────────────────────────────────
    def run(self):
        """Main game loop."""
        if self.event_bus:
            from It1_interfaces.EventTypes import GAME_STARTED
            self.event_bus.publish(GAME_STARTED, {"time": self.game_time_ms()})
        self.start_user_input_thread()

        start_ms = self.game_time_ms()
        for p in self.pieces.values():
            p.reset(start_ms)

        # ─────── main loop ──────────────────────────────────────────────────
        while not self._is_win() and not getattr(self, '_should_quit', False):
            now = self.game_time_ms()

            # (1) Update physics & animations
            for p in self.pieces.values():
                p.update(now)

            # (2) Handle queued Commands from input thread
            while not self.user_input_queue.empty():
                cmd: Command = self.user_input_queue.get()
                self._process_input(cmd)
                if self.event_bus:
                    from It1_interfaces.EventTypes import MOVE_DONE
                    self.event_bus.publish(MOVE_DONE, {"command": cmd})

            # (3) Draw current position
            self._draw()
            if not self._show():  # Returns False if user closed window
                break

            # (4) Detect captures
            self._resolve_collisions()

        if self.event_bus:
            from It1_interfaces.EventTypes import GAME_ENDED
            self.event_bus.publish(GAME_ENDED, {"time": self.game_time_ms()})
        self._announce_win()
        cv2.destroyAllWindows()

    # ─── drawing helpers ────────────────────────────────────────────────────
    def _process_input(self, cmd: Command):
        """Process player input commands."""
        if cmd.piece_id in self.pieces:
            self.pieces[cmd.piece_id].on_command(cmd)

    

    def _show(self) -> bool:
        """Show the current frame and handle window events."""
        if hasattr(self, 'current_display'):
            cv2.imshow("Kung Fu Chess", self.current_display.img)
            return cv2.waitKey(1) & 0xFF != 27  # Return False if ESC pressed
        return True

    # ─── capture resolution ────────────────────────────────────────────────
    def _resolve_collisions(self):
        """Resolve piece collisions and captures."""
        positions: Dict[tuple, List[Piece]] = {}
        to_remove = []

        # Group pieces by their positions
        for piece in self.pieces.values():
            pos = piece.current_state.physics.get_pos()
            if pos not in positions:
                positions[pos] = []
            positions[pos].append(piece)

        # Resolve collisions
        for pos, pieces_in_cell in positions.items():
            if len(pieces_in_cell) > 1:
                survivor = pieces_in_cell[0]
                for p in pieces_in_cell[1:]:
                    to_remove.append(p)

        # Remove captured pieces
        for p in to_remove:
            if self.event_bus:
                from It1_interfaces.EventTypes import PIECE_CAPTURED
                self.event_bus.publish(PIECE_CAPTURED, {"piece": p})
            del self.pieces[p.piece_id]

    # ─── board validation & win detection ───────────────────────────────────
    def _is_win(self) -> bool:
        """Check if the game has ended."""
        kings = [p for p in self.pieces.values() if p.piece_type == "King"]
        return False  # Temporary override to allow the game to continue

    def _announce_win(self):
        """Announce the winner."""
        kings = [p for p in self.pieces.values() if p.piece_type == "King"]
        if len(kings) == 1:
            print(f"Game Over! {kings[0].color} wins!")
        else:
            print("Game Over! It's a draw.")
        print("Game Over! Press any key to close the window.")
        cv2.waitKey(0)  # Wait for a key press before closing the window

    def _move_selection(self, player, direction):
        # Move the selection cursor for the given player
        pos = self.selection[player]['pos']
        if direction == 'up' and pos[0] > 0:
            pos[0] -= 1
        elif direction == 'down' and pos[0] < self.board.H_cells - 1:
            pos[0] += 1
        elif direction == 'left' and pos[1] > 0:
            pos[1] -= 1
        elif direction == 'right' and pos[1] < self.board.W_cells - 1:
            pos[1] += 1

    def _select_piece(self, player):
        # Select or move a piece for the given player
        pos = tuple(self.selection[player]['pos'])
        selected = self.selection[player]['selected']
        if selected is None:
            # First keypress: select a piece at the cursor
            for piece in self.pieces.values():
                p_pos = tuple(piece.current_state.physics.current_cell)
                if p_pos == pos:
                    self.selection[player]['selected'] = piece
                    break
        else:
            # Second keypress: try to move selected piece to cursor position
            start_pos = tuple(selected.current_state.physics.current_cell)
            moves = selected.current_state.moves
            allowed = False
            for move in getattr(moves, 'move_list', []):
                target = (start_pos[0] + move[0], start_pos[1] + move[1])
                if target == pos:
                    allowed = True
                    break
            if allowed:
                now = self.game_time_ms()
                cmd = Command.create_move_command(now, selected.piece_id, start_pos, pos)
                self.user_input_queue.put(cmd)
            # Deselect after attempt
            self.selection[player]['selected'] = None
