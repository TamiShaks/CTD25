import queue
import threading
import pygame
import time
from typing import Dict, Tuple, Optional
from Command import Command
from ChessRulesValidator import ChessRulesValidator
from EventTypes import INVALID_MOVE, PAWN_PROMOTION


class ThreadedInputManager(threading.Thread):
    """Threaded input manager that runs parallel to the game and listens for input."""
    
    def __init__(self, board, user_input_queue: queue.Queue, event_bus=None, debug=False):
        """Initialize the threaded input manager."""
        super().__init__(daemon=True)
        self.board = board
        self.user_input_queue = user_input_queue
        self.event_bus = event_bus
        self.chess_validator = ChessRulesValidator()
        self.debug = debug
        
        # Network game settings
        self.is_network_game = False
        self.my_player_color = None  # 'white' or 'black' for network games
        
        # Player selections
        self.selection = {
            'A': {'pos': [0, 0], 'selected': None, 'color': (255, 0, 0)},
            'B': {'pos': [7, 7], 'selected': None, 'color': (0, 0, 255)}
        }
        
        # Promotion state
        self.promotion_state = {
            'A': self._create_promotion_state(),
            'B': self._create_promotion_state()
        }
        self.promotion_options = ["Q", "R", "B", "N"]
        
        # Thread control
        self._running = False
        self._pieces_ref = None
        self._game_time_func = None
        self._last_key_time = {}
        self._key_repeat_delay = 0.25
    
    def _create_promotion_state(self) -> Dict:
        """Create initial promotion state for a player."""
        return {
            'active': False, 'pending': False, 'piece': None, 
            'target_pos': None, 'menu_selection': 0, 'pending_since': 0
        }
        
    def set_game_references(self, pieces_dict, game_time_func):
        """Set references to game pieces and time function."""
        self._pieces_ref = pieces_dict
        self._game_time_func = game_time_func
    
    def set_network_settings(self, is_network_game: bool, my_player_color: str = None):
        """Set network game settings."""
        self.is_network_game = is_network_game
        self.my_player_color = my_player_color  # 'white' or 'black'
        
        if self.debug and is_network_game:
            print(f"🌐 Network mode: Playing as {my_player_color}")
            print(f"🎮 Network Game Status: {'ONLINE' if is_network_game else 'LOCAL'}")
        elif self.debug:
            print(f"🎮 Game Mode: LOCAL (both players on same computer)")
    
    def _can_player_control_piece(self, player: str, piece) -> bool:
        """Check if a player can control a specific piece."""
        if not self.is_network_game:
            # In local games, both players can control any piece
            return True
        
        # In network games, restrict based on color
        if not hasattr(piece, 'color'):
            return True  # Allow if piece has no color attribute
        
        # Map network player color to local player behavior
        if self.my_player_color == 'white':
            # If I'm the white player, I can only control white pieces
            # This means I behave like player A (who controls white pieces)
            player_can_control_white = True
            player_can_control_black = False
        elif self.my_player_color == 'black':
            # If I'm the black player, I can only control black pieces  
            # This means I behave like player B (who controls black pieces)
            player_can_control_white = False
            player_can_control_black = True
        else:
            return True  # Default allow if color not set
            
        # Check if the piece color matches what this player can control
        if piece.color == "White":
            return player_can_control_white
        elif piece.color == "Black":
            return player_can_control_black
            
        return True  # Default allow for pieces without clear color
        
    def start_listening(self):
        """Start the input listening thread."""
        self._running = True
        self.start()
        
    def stop_listening(self):
        """Stop the input listening thread."""
        self._running = False
        
    def check_pending_promotions(self):
        """Check if any pending promotions should be activated."""
        if not self._pieces_ref or not self._game_time_func:
            return
            
        now = self._game_time_func()
        
        for player in ['A', 'B']:
            state = self.promotion_state[player]
            if state['pending'] and not state['active']:
                piece = state['piece']
                target_pos = state['target_pos']
                
                # Check if piece has reached target position and is not moving
                if (piece and 
                    hasattr(piece, 'current_state') and 
                    hasattr(piece.current_state, 'physics')):
                    
                    current_pos = piece.current_state.physics.current_cell
                    is_moving = piece.current_state.physics.is_moving
                    
                    # If piece reached target and stopped moving, activate promotion
                    if (current_pos == target_pos and 
                        not is_moving and 
                        now - state['pending_since'] > 500):  # 500ms delay to ensure movement/combat completed
                        
                        # Activate promotion menu
                        state['active'] = True
                        state['pending'] = False
                        state['menu_selection'] = 0
                        
                        # Publish promotion event
                        if self.event_bus:
                            self.event_bus.publish(PAWN_PROMOTION, {
                                "player": player,
                                "piece_id": piece.piece_id,
                                "from_pos": target_pos,  # Now they're the same
                                "to_pos": target_pos,
                                "options": self.promotion_options
                            })
                        
                        print(f" Player {player}: Pawn promotion! Select your piece.")
                        break
        
    def _get_key_mappings(self) -> Dict:
        """Get the key mapping configuration."""
        # In network mode, map keys based on player color
        if self.is_network_game:
            if self.my_player_color == 'white':
                # White player uses arrows (like player A)
                return {
                    pygame.K_ESCAPE: ('SYSTEM', 'QUIT'),
                    pygame.K_TAB: ('SYSTEM', 'SHOW_STATS'),
                    pygame.K_UP: ('A', 'up'),
                    pygame.K_DOWN: ('A', 'down'),
                    pygame.K_LEFT: ('A', 'left'),
                    pygame.K_RIGHT: ('A', 'right'),
                    pygame.K_RETURN: ('A', 'select'),
                    # Disable WASD for white player
                }
            elif self.my_player_color == 'black':
                # Black player uses WASD (like player B)  
                return {
                    pygame.K_ESCAPE: ('SYSTEM', 'QUIT'),
                    pygame.K_TAB: ('SYSTEM', 'SHOW_STATS'),
                    pygame.K_w: ('B', 'up'),
                    pygame.K_s: ('B', 'down'),
                    pygame.K_a: ('B', 'left'),
                    pygame.K_d: ('B', 'right'),
                    pygame.K_SPACE: ('B', 'select'),
                    # Disable arrows for black player
                }
        
        # Default local game mapping
        return {
            pygame.K_ESCAPE: ('SYSTEM', 'QUIT'),
            pygame.K_TAB: ('SYSTEM', 'SHOW_STATS'),
            pygame.K_UP: ('A', 'up'),
            pygame.K_DOWN: ('A', 'down'),
            pygame.K_LEFT: ('A', 'left'),
            pygame.K_RIGHT: ('A', 'right'),
            pygame.K_RETURN: ('A', 'select'),
            pygame.K_w: ('B', 'up'),
            pygame.K_s: ('B', 'down'),
            pygame.K_a: ('B', 'left'),
            pygame.K_d: ('B', 'right'),
            pygame.K_SPACE: ('B', 'select'),
        }
    
    def _handle_system_command(self, action: str, current_time: float):
        """Handle system commands like QUIT and SHOW_STATS."""
        if action == 'QUIT':
            self.user_input_queue.put(Command(
                timestamp=int(current_time * 1000),
                piece_id="SYSTEM",
                type="QUIT",
                params=[]
            ))
            self._running = False
        elif action == 'SHOW_STATS':
            self.user_input_queue.put(Command(
                timestamp=int(current_time * 1000),
                piece_id="SYSTEM",
                type="SHOW_STATS",
                params=[]
            ))
    
    def _handle_player_action(self, player: str, action: str):
        """Handle player actions (movement, selection, promotion)."""
        # In network mode, restrict player actions based on their color
        if self.is_network_game and self.my_player_color:
            # Map network color to local player
            if self.my_player_color == 'white' and player != 'A':
                return  # White player can only control Player A (white pieces)
            elif self.my_player_color == 'black' and player != 'B':
                return  # Black player can only control Player B (black pieces)
        
        if self.promotion_state[player]['active']:
            if self.debug:
                print(f"PROMOTION DEBUG: Player {player} pressed {action}")
            if action in ['left', 'right']:
                self._handle_promotion_navigation(player, action)
            elif action == 'select':
                self._confirm_promotion(player)
        else:
            # Normal gameplay
            if action == 'select':
                self._select_piece(player)
            else:
                self._move_selection(player, action)

    def run(self):
        """Main thread loop - listens for input continuously using key polling."""
        print("Input thread started - listening for player input...")
        
        while self._running:
            try:
                current_time = time.time()
                keys = pygame.key.get_pressed()
                
                self.check_pending_promotions()
                
                for key_code, (player_or_system, action) in self._get_key_mappings().items():
                    if keys[key_code]:
                        # Check repeat delay
                        if (key_code in self._last_key_time and 
                            current_time - self._last_key_time[key_code] < self._key_repeat_delay):
                            continue
                        
                        self._last_key_time[key_code] = current_time
                        
                        # Handle the key press
                        if player_or_system == 'SYSTEM':
                            self._handle_system_command(action, current_time)
                            if action == 'QUIT':
                                break
                        else:
                            self._handle_player_action(player_or_system, action)
                
                time.sleep(0.01)  # 10ms sleep = ~100 FPS input polling
                
            except Exception as e:
                print(f"Input thread error: {e}")
                time.sleep(0.1)
                
        print("Input thread stopped.")
        
    def _move_selection(self, player: str, direction: str):
        """Move the selection cursor for the given player."""
        pos = self.selection[player]['pos']
        old_pos = pos.copy()

        if direction == 'up' and pos[0] > 0:
            pos[0] -= 1
        elif direction == 'down' and pos[0] < self.board.H_cells - 1:
            pos[0] += 1
        elif direction == 'left' and pos[1] > 0:
            pos[1] -= 1
        elif direction == 'right' and pos[1] < self.board.W_cells - 1:
            pos[1] += 1
            
        if old_pos != pos and self.debug:
            print(f"Player {player}: {old_pos} → {pos}")

    def _select_piece(self, player: str):
        """Select or move a piece for the given player."""
        if not self._pieces_ref or not self._game_time_func:
            return  # Game references not set yet
            
        pos = tuple(self.selection[player]['pos'])
        selected = self.selection[player]['selected']

        if selected is None:
            self._try_select_piece_at_position(player, pos)
        else:
            self._try_move_selected_piece(player, selected, pos)

    def _try_select_piece_at_position(self, player: str, pos: tuple):
        """Try to select a piece at the given position."""
        # Determine which pieces this player can select
        if self.is_network_game:
            # In network mode, restrict based on assigned player color
            if self.my_player_color == 'white':
                # White player can only select white pieces (like player A)
                allowed_piece_color = "White" 
            elif self.my_player_color == 'black':
                # Black player can only select black pieces (like player B)
                allowed_piece_color = "Black"
            else:
                # Fallback if color not set
                allowed_piece_color = "White" if player == "A" else "Black"
        else:
            # In local mode, use traditional player mapping  
            allowed_piece_color = "White" if player == "A" else "Black"
        
        # Find piece at position with correct color
        for piece in self._pieces_ref.values():
            p_pos = tuple(piece.current_state.physics.current_cell)
            
            # Check position and color match
            if p_pos == pos and hasattr(piece, 'color') and piece.color == allowed_piece_color:
                self.selection[player]['selected'] = piece
                if self.debug:
                    if self.is_network_game:
                        print(f" ✅ Player {player} (my_color={self.my_player_color}) selected {piece.piece_id} (piece_color={piece.color}) at {pos}")
                    else:
                        print(f" ✅ Player {player} selected {piece.piece_id} (piece_color={piece.color}) at {pos}")
                return
        
        # No valid piece found - show restriction message
        if self.debug:
            if self.is_network_game:
                print(f" ❌ No {allowed_piece_color} piece at {pos} for player {player} (my_color={self.my_player_color})")
            else:
                print(f" ❌ No {allowed_piece_color} piece at {pos} for player {player}")
                
        # Always show restriction message in network mode for clarity
        if self.is_network_game:
            print(f" 🚫 Network restriction: You can only move {allowed_piece_color.lower()} pieces!")

    def _try_move_selected_piece(self, player: str, selected, pos: tuple):
        """Try to move the selected piece to the given position."""
        start_pos = tuple(selected.current_state.physics.current_cell)
        
        if start_pos == pos:
            self._handle_jump_action(player, selected, pos)
            return
            
        if self._is_move_allowed(selected, start_pos, pos):
            self._execute_validated_move(player, selected, start_pos, pos)
        else:
            self._handle_invalid_move(player, selected, start_pos, pos, "Not a valid move")
        
        self.selection[player]['selected'] = None

    def _handle_jump_action(self, player: str, selected, pos: tuple):
        """Handle jump action when selecting same position."""
        now = self._game_time_func()
        cmd = Command.create_jump_command(now, selected.piece_id, pos, pos)
        self.user_input_queue.put(cmd)
        print(f"🦘 Player {player}: {selected.piece_id} jumps at {pos}")
        self.selection[player]['selected'] = None

    def _is_move_allowed(self, selected, start_pos: tuple, target_pos: tuple) -> bool:
        """Check if the move is allowed by piece movement rules."""
        moves = selected.current_state.moves
        valid_moves = moves.get_moves(start_pos[0], start_pos[1])
        return target_pos in valid_moves

    def _execute_validated_move(self, player: str, selected, start_pos: tuple, pos: tuple):
        """Execute a move after validating chess rules."""
        target_piece = self._find_piece_at_position(pos)
        
        if self.chess_validator.is_valid_move(selected, start_pos, pos, target_piece, self._pieces_ref):
            if self.chess_validator.is_pawn_promotion(selected, pos):
                self._handle_pawn_promotion_move(player, selected, start_pos, pos)
            else:
                self._execute_regular_move(player, selected, start_pos, pos)
        else:
            self._handle_invalid_move(player, selected, start_pos, pos, "Invalid chess rule")

    def _find_piece_at_position(self, pos: tuple):
        """Find a piece at the given position."""
        for piece in self._pieces_ref.values():
            if tuple(piece.current_state.physics.current_cell) == pos:
                return piece
        return None

    def _handle_pawn_promotion_move(self, player: str, selected, start_pos: tuple, pos: tuple):
        """Handle a pawn promotion move."""
        now = self._game_time_func()
        cmd = Command.create_move_command(now, selected.piece_id, start_pos, pos)
        self.user_input_queue.put(cmd)
        print(f"Player {player}: {selected.piece_id} {start_pos} → {pos} (moving for promotion)")
        
        # Mark promotion as pending
        self.promotion_state[player]['pending'] = True
        self.promotion_state[player]['piece'] = selected
        self.promotion_state[player]['target_pos'] = pos
        self.promotion_state[player]['pending_since'] = now
        
        print(f" Player {player}: Pawn promotion pending - waiting for movement to complete")

    def _execute_regular_move(self, player: str, selected, start_pos: tuple, pos: tuple):
        """Execute a regular move."""
        now = self._game_time_func()
        cmd = Command.create_move_command(now, selected.piece_id, start_pos, pos)
        self.user_input_queue.put(cmd)
        print(f" Player {player}: {selected.piece_id} {start_pos} → {pos}")

    def _handle_invalid_move(self, player: str, selected, start_pos: tuple, pos: tuple, reason: str):
        """Handle an invalid move by publishing event and logging."""
        if self.event_bus:
            self.event_bus.publish(INVALID_MOVE, {
                "player": player,
                "piece_id": selected.piece_id,
                "from_pos": start_pos,
                "to_pos": pos,
                "reason": reason
            })
        if self.debug:
            print(f" {reason}: {selected.piece_id} {start_pos} → {pos}")
    
    def get_selection(self, player: str) -> Dict:
        """Get the current selection for a player."""
        return self.selection[player]
    
    def get_all_selections(self) -> Dict:
        """Get all player selections."""
        return self.selection
    
    def _handle_promotion_navigation(self, player: str, direction: str):
        """Handle navigation in promotion menu."""
        if not self.promotion_state[player]['active']:
            return
            
        print(f" PROMOTION NAV: Player {player} direction {direction}, current={self.promotion_state[player]['menu_selection']}")
            
        if direction == 'left' and self.promotion_state[player]['menu_selection'] > 0:
            self.promotion_state[player]['menu_selection'] -= 1
            print(f" Player {player}: Promotion menu ← {self.promotion_options[self.promotion_state[player]['menu_selection']]}")
        elif direction == 'right' and self.promotion_state[player]['menu_selection'] < len(self.promotion_options) - 1:
            self.promotion_state[player]['menu_selection'] += 1
            print(f" Player {player}: Promotion menu → {self.promotion_options[self.promotion_state[player]['menu_selection']]}")
        else:
            print(f" PROMOTION NAV: No movement possible - at edge or invalid direction")
    
    def _confirm_promotion(self, player: str):
        """Confirm promotion choice and execute the move."""
        if not self.promotion_state[player]['active']:
            return
            
        selected_piece = self.promotion_state[player]['piece']
        target_pos = self.promotion_state[player]['target_pos']
        start_pos = tuple(selected_piece.current_state.physics.current_cell)
        promotion_choice = self.promotion_options[self.promotion_state[player]['menu_selection']]
        
        # Create promotion command
        now = self._game_time_func()
        cmd = Command.create_promotion_command(now, selected_piece.piece_id, start_pos, target_pos, promotion_choice)
        self.user_input_queue.put(cmd)
        
        print(f" Player {player}: Promoted {selected_piece.piece_id} to {promotion_choice} at {target_pos}")
        
        # Reset promotion state
        self.promotion_state[player]['active'] = False
        self.promotion_state[player]['pending'] = False
        self.promotion_state[player]['piece'] = None
        self.promotion_state[player]['target_pos'] = None
        self.promotion_state[player]['menu_selection'] = 0
        self.promotion_state[player]['pending_since'] = 0
    
    def get_promotion_state(self, player: str) -> Dict:
        """Get current promotion state for player."""
        if player in self.promotion_state:
            return self.promotion_state[player]
        else:
            # Return default state if player not found
            return {'active': False, 'piece': None, 'target_pos': None, 'menu_selection': 0}
