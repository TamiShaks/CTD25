import pygame
import queue, threading, time, math
import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
from Board import Board
from Command import Command
from Piece import Piece
from img import Img
from GameUI import GameUI
from StatisticsManager import StatisticsManager
from ThreadedInputManager import ThreadedInputManager
from PromotionUI import PromotionUI
from PromotionManager import PromotionManager
from CollisionManager import CollisionManager
from EventTypes import GAME_STARTED, GAME_ENDED, MOVE_DONE, PIECE_CAPTURED, PAWN_PROMOTION


class InvalidBoard(Exception): ...
# ────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self, pieces: List[Piece], board: Board, event_bus=None, score_manager=None, move_logger=None):
        """Initialize the game with pieces, board, and optional event bus and managers."""
        # Core game components
        self.pieces = {p.piece_id: p for p in pieces}
        self.board = board
        self.start_time = time.time()
        
        # Event handling and game state
        self.user_input_queue = queue.Queue()
        self.event_bus = event_bus
        self._should_quit = False
        
        # Game managers
        self.score_manager = score_manager
        self.move_logger = move_logger
        self.statistics_manager = StatisticsManager()
        self.input_manager = ThreadedInputManager(board, self.user_input_queue, event_bus, debug=True)
        self.promotion_manager = PromotionManager(board)
        self.collision_manager = CollisionManager(event_bus)

        # Network functionality (optional)
        self.network_manager = None

        # Display settings
        self.cell_width = self.board.cell_W_pix
        self.cell_height = self.board.cell_H_pix
        self.info_panel_width = 300
        self.board_width = self.board.W_cells * self.cell_width
        self.board_height = self.board.H_cells * self.cell_height
        self.window_width = self.board_width + (2 * self.info_panel_width)
        self.window_height = self.board_height
        
        # Initialize pygame and UI components
        self._init_pygame_window()
        self.ui = GameUI(self.info_panel_width)
        self.promotion_ui = PromotionUI(self.window_width, self.window_height)

    # ─── helpers ─────────────────────────────────────────────────────────────
    def game_time_ms(self) -> int:
        """Return the current game time in milliseconds."""
        return int((time.time() - self.start_time) * 1000)

    def _init_pygame_window(self):
        """Initialize pygame and create the main window."""
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Kung Fu Chess")
        self.clock = pygame.time.Clock()

    def clone_board(self) -> Board:
        """
        Return a **brand-new** Board wrapping a copy of the background pixels
        so we can paint sprites without touching the pristine board.
        """
        return self.board.clone()

    def _draw(self):
        """Draw the current game state with info panel."""
        # Clear screen with black background
        self.screen.fill((0, 0, 0))
        
        # Draw game board
        board_img = self.clone_board().img
        for piece in self.pieces.values():
            piece.render_piece_on_board(board_img, self.game_time_ms())
        
        # Get player selections once
        selection = self.input_manager.get_all_selections()

# Convert board image to RGB for pygame
        
        # Handle both BGR and BGRA images
        if board_img.img.shape[2] == 4:
            img_rgb = cv2.cvtColor(board_img.img, cv2.COLOR_BGRA2RGB)
        else:
            img_rgb = cv2.cvtColor(board_img.img, cv2.COLOR_BGR2RGB)
            
        # Create pygame surface with proper orientation
        pygame_surface = pygame.surfarray.make_surface(img_rgb.swapaxes(0, 1))

# draw the selection rectangles
        for player in ['A', 'B']:
            pos = selection[player]['pos']
            color = selection[player]['color']
            rect = pygame.Rect(pos[1] * self.cell_width, pos[0] * self.cell_height,
                               self.cell_width, self.cell_height)
            pygame.draw.rect(pygame_surface, color, rect, 3)
            selected_piece = selection[player]['selected']
            if selected_piece:
                p_pos = selected_piece.current_state.physics.current_cell
                rect2 = pygame.Rect(p_pos[1] * self.cell_width, p_pos[0] * self.cell_height,
                                    self.cell_width, self.cell_height)
                pygame.draw.rect(pygame_surface, color, rect2, 5)

# showing the board in the center of the screen
        board_x_offset = self.info_panel_width  
        self.screen.blit(pygame_surface, (board_x_offset, 0))
        
# draw the data with GameUI
        self.ui.draw_player_panels(self.screen, self.board_width, self.window_height, 
                                  self.pieces, selection, self.start_time, 
                                  self.score_manager, self.move_logger)
        
        # Draw promotion popup if active for any player
        for player in ['A', 'B']:
            promotion_state = self.input_manager.get_promotion_state(player)
            if promotion_state['active']:
                self.promotion_ui.draw_promotion_popup(
                    self.screen, 
                    player, 
                    promotion_state['menu_selection'], 
                    self.input_manager.promotion_options
                )
        
        pygame.display.flip()

    # ─── main public entrypoint ──────────────────────────────────────────────
    def run(self):
        """Main game loop."""
        if self.event_bus:
            self.event_bus.publish(GAME_STARTED, {"time": self.game_time_ms()})
        print("Game started. Press ESC to exit at any time.")

        start_ms = self.game_time_ms()
        for p in self.pieces.values():
            p.reset_piece_to_initial_state(start_ms)

        # ═══════════ START THREADED INPUT MANAGER ═══════════
        self.input_manager.set_game_references(self.pieces, self.game_time_ms)
        
        # Configure network settings if in network mode
        if self.network_manager:
            network_status = self.network_manager.get_network_status()
            self.input_manager.set_network_settings(
                is_network_game=network_status['is_network_game'],
                my_player_color=network_status['my_color']
            )
        
        self.input_manager.start_listening()
        print("Started threaded input manager")

        # ─────── main loop ──────────────────────────────────────────────────
        while not self._is_win() and not self._should_quit:
            now = self.game_time_ms()

            # (0) Update network manager if present
            if self.network_manager:
                self.network_manager.update()

            # (1) Update physics & animations
            for p in self.pieces.values():
                p.update_piece_state(now)

            # (1.5) Handle pygame QUIT events (window close button)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._should_quit = True

            # (2) Handle queued Commands from input thread
            while not self.user_input_queue.empty():
                cmd: Command = self.user_input_queue.get()
                
                # Handle system commands
                if cmd.piece_id == "SYSTEM":
                    if cmd.type == "QUIT":
                        self._should_quit = True
                        continue
                    elif cmd.type == "SHOW_STATS":
                        self.statistics_manager.display_live_statistics(self.pieces, self.start_time)
                        continue
                
                # Handle game commands
                if cmd.type == "Promotion":
                    self._handle_promotion_command(cmd)
                else:
                    self._process_input(cmd)
                
                if self.event_bus:
                    self.event_bus.publish(MOVE_DONE, {"command": cmd})

            # (3) Draw current position
            self._draw()

            # (4) Detect captures
            self._resolve_collisions()


            self.clock.tick(30)

        # ═══════════ STOP THREADED INPUT MANAGER ═══════════
        self.input_manager.stop_listening()
        print("Stopped threaded input manager")

        # Stop network manager if present
        if self.network_manager:
            self.network_manager.stop_network_game()

        if self.event_bus:
            self.event_bus.publish(GAME_ENDED, {"time": self.game_time_ms()})
        
        # Display final statistics before announcing winner
        self.statistics_manager.display_final_statistics(self.pieces, self.start_time)
        
        self._announce_win()
        pygame.quit()

    # ─── drawing helpers ────────────────────────────────────────────────────
    def _process_input(self, cmd: Command):
        """Process player input commands."""
        if cmd.piece_id in self.pieces:
            now = self.game_time_ms()
            piece = self.pieces[cmd.piece_id]
            piece.handle_command(cmd, now)
        else:
            pass  # Piece not found - silently ignore
    


    def _handle_promotion_command(self, cmd: Command):
        """Handle pawn promotion command - replace the piece with a new one."""
        self.promotion_manager.handle_promotion(cmd, self.pieces, self.input_manager, self.game_time_ms)
    # ─── capture resolution ────────────────────────────────────────────────
    def _resolve_collisions(self):
        """Resolve piece collisions and captures based on chess-like rules."""
        self.collision_manager.resolve_collisions(self.pieces, self.game_time_ms)



    # ─── board validation & win detection ───────────────────────────────────
    def _get_kings(self) -> list:
        """Get all kings currently on the board."""
        return [p for p in self.pieces.values() if p.piece_type == "K"]

    def _is_win(self) -> bool:
        """Check if the game has ended."""
        # Game ends when one or both kings are captured
        return len(self._get_kings()) < 2

    def _announce_win(self):
        """Announce the winner."""
        kings = self._get_kings()
        if len(kings) == 1:
            # One king survived - that color wins
            winner_color = kings[0].color
            print(f" Game Over! {winner_color} wins! ")
            print(f"The {winner_color} king survived and conquered the battlefield!")
        elif len(kings) == 0:
            # Both kings are dead - it's a draw
            print(" Game Over! Both kings have fallen - It's a draw! ")
        else:
            # This shouldn't happen in normal gameplay
            print("Game Over! Unexpected end condition.")
        
        print("Press any key to close the window.")
        # Wait for key press using pygame instead of cv2.waitKey
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                    waiting = False
                    