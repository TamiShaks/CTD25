import queue
import threading
import pygame
import time
from typing import Dict, Tuple, Optional
from It1_interfaces.Command import Command
from It1_interfaces.ChessRulesValidator import ChessRulesValidator
from It1_interfaces.EventTypes import INVALID_MOVE, PAWN_PROMOTION


class ThreadedInputManager(threading.Thread):
    """Threaded input manager that runs parallel to the game and listens for input."""
    
    def __init__(self, board, user_input_queue: queue.Queue, event_bus=None, debug=False):
        """Initialize the threaded input manager."""
        super().__init__(daemon=True)  # Daemon thread - dies when main program exits
        self.board = board
        self.user_input_queue = user_input_queue
        self.event_bus = event_bus
        self.chess_validator = ChessRulesValidator()
        self.debug = debug  # Control debug output
        self.selection = {
            'A': {'pos': [0, 0], 'selected': None, 'color': (255, 0, 0)},
            'B': {'pos': [7, 7], 'selected': None, 'color': (0, 0, 255)}
        }
        
        # Promotion state tracking
        self.promotion_state = {
            'A': {'active': False, 'pending': False, 'piece': None, 'target_pos': None, 'menu_selection': 0, 'pending_since': 0},
            'B': {'active': False, 'pending': False, 'piece': None, 'target_pos': None, 'menu_selection': 0, 'pending_since': 0}
        }
        self.promotion_options = ["Q", "R", "B", "N"]  # Queen, Rook, Bishop, Knight
        
        # Thread control
        self._running = False
        self._pieces_ref = None
        self._game_time_func = None
        
        # Input state tracking
        self._last_key_time = {}
        self._key_repeat_delay = 0.25  # 250ms between key repeats (slower)
        
    def set_game_references(self, pieces_dict, game_time_func):
        """Set references to game pieces and time function."""
        self._pieces_ref = pieces_dict
        self._game_time_func = game_time_func
        
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
                        
                        print(f"🎯 Player {player}: Pawn promotion! Select your piece.")
                        break
        
    def run(self):
        """Main thread loop - listens for input continuously using key polling."""
        print("🎮 Input thread started - listening for player input...")
        
        while self._running:
            try:
                current_time = time.time()
                keys = pygame.key.get_pressed()
                
                # Check for pending promotions that should be activated
                self.check_pending_promotions()
                
                # Check each key and handle if pressed (with repeat delay)
                key_mappings = {
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
                
                for key_code, (player_or_system, action) in key_mappings.items():
                    if keys[key_code]:
                        # Check if enough time has passed since last press
                        if key_code in self._last_key_time:
                            if current_time - self._last_key_time[key_code] < self._key_repeat_delay:
                                continue
                        
                        self._last_key_time[key_code] = current_time
                        
                        # Handle the key press
                        if player_or_system == 'SYSTEM':
                            if action == 'QUIT':
                                self.user_input_queue.put(Command(
                                    timestamp=int(current_time * 1000),
                                    piece_id="SYSTEM",
                                    type="QUIT",
                                    params=[]
                                ))
                                self._running = False
                                break
                            elif action == 'SHOW_STATS':
                                self.user_input_queue.put(Command(
                                    timestamp=int(current_time * 1000),
                                    piece_id="SYSTEM",
                                    type="SHOW_STATS",
                                    params=[]
                                ))
                        else:
                            # Player action
                            # Check if player is in promotion mode
                            if self.promotion_state[player_or_system]['active']:
                                print(f"🔥 PROMOTION DEBUG: Player {player_or_system} pressed {action}")
                                if action in ['left', 'right']:
                                    self._handle_promotion_navigation(player_or_system, action)
                                elif action == 'select':
                                    self._confirm_promotion(player_or_system)
                            else:
                                # Normal gameplay
                                if action == 'select':
                                    self._select_piece(player_or_system)
                                else:
                                    self._move_selection(player_or_system, action)
                
                # Small sleep to prevent excessive CPU usage
                time.sleep(0.01)  # 10ms sleep = ~100 FPS input polling
                
            except Exception as e:
                print(f"⚠️ Input thread error: {e}")
                time.sleep(0.1)
                
        print("🎮 Input thread stopped.")
        
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
            
            # Only print when cursor actually moves (less noise)
        if old_pos != pos and self.debug:
            print(f"🎮 Player {player}: {old_pos} → {pos}")

    def _select_piece(self, player: str):
        """Select or move a piece for the given player."""
        if not self._pieces_ref or not self._game_time_func:
            return  # Game references not set yet
            
        pos = tuple(self.selection[player]['pos'])
        selected = self.selection[player]['selected']
        player_color = "White" if player == "A" else "Black"

        if selected is None:
            # First keypress: select a piece at the cursor that belongs to this player
            for piece in self._pieces_ref.values():
                p_pos = tuple(piece.current_state.physics.current_cell)
                if p_pos == pos and hasattr(piece, 'color') and piece.color == player_color:
                    self.selection[player]['selected'] = piece
                    if self.debug:
                        print(f"🎯 Player {player} selected {piece.piece_id} at {pos}")
                    break
            else:
                if self.debug:
                    print(f"❌ No {player_color} piece at {pos}")
        else:
            # Second keypress: try to move selected piece to cursor position
            start_pos = tuple(selected.current_state.physics.current_cell)
            
            if start_pos == pos:
                # Same position - make the piece JUMP instead of deselecting!
                now = self._game_time_func()
                cmd = Command.create_jump_command(now, selected.piece_id, pos, pos)
                self.user_input_queue.put(cmd)
                print(f"🦘 Player {player}: {selected.piece_id} jumps at {pos}")
                self.selection[player]['selected'] = None
                return
                
            moves = selected.current_state.moves
            valid_moves = moves.get_moves(start_pos[0], start_pos[1])
            
            allowed = False
            for move in valid_moves:
                if move == pos:
                    allowed = True
                    break
            if allowed:
                # Check chess rules using validator
                target_piece = None
                for piece in self._pieces_ref.values():
                    if tuple(piece.current_state.physics.current_cell) == pos:
                        target_piece = piece
                        break
                
                # Use chess validator to check all rules
                if self.chess_validator.is_valid_move(selected, start_pos, pos, target_piece, self._pieces_ref):
                    # Check if this is a pawn promotion
                    if self.chess_validator.is_pawn_promotion(selected, pos):
                        # First execute the move (pawn moves to end and captures if needed)
                        now = self._game_time_func()
                        cmd = Command.create_move_command(now, selected.piece_id, start_pos, pos)
                        self.user_input_queue.put(cmd)
                        print(f"✅ Player {player}: {selected.piece_id} {start_pos} → {pos} (moving for promotion)")
                        
                        # Mark promotion as pending - will be activated after capture/movement completes
                        self.promotion_state[player]['pending'] = True
                        self.promotion_state[player]['piece'] = selected
                        self.promotion_state[player]['target_pos'] = pos
                        self.promotion_state[player]['pending_since'] = now
                        
                        print(f"🎯 Player {player}: Pawn promotion pending - waiting for movement to complete")
                    else:
                        # Regular move
                        now = self._game_time_func()
                        cmd = Command.create_move_command(now, selected.piece_id, start_pos, pos)
                        self.user_input_queue.put(cmd)
                        print(f"✅ Player {player}: {selected.piece_id} {start_pos} → {pos}")  # Always show successful moves
                else:
                    # Send INVALID_MOVE event to trigger fail sound
                    if self.event_bus:
                        self.event_bus.publish(INVALID_MOVE, {
                            "player": player,
                            "piece_id": selected.piece_id,
                            "from_pos": start_pos,
                            "to_pos": pos,
                            "reason": "Invalid chess rule"
                        })
                    if self.debug:
                        print(f"❌ Invalid chess rule: {selected.piece_id} {start_pos} → {pos}")
            else:
                # Send INVALID_MOVE event to trigger fail sound
                if self.event_bus:
                    self.event_bus.publish(INVALID_MOVE, {
                        "player": player,
                        "piece_id": selected.piece_id,
                        "from_pos": start_pos,
                        "to_pos": pos,
                        "reason": "Not a valid move"
                    })
                if self.debug:
                    print(f"⚠️ Not a valid move: {selected.piece_id} {start_pos} → {pos}")
            self.selection[player]['selected'] = None
    
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
            
        print(f"🔥 PROMOTION NAV: Player {player} direction {direction}, current={self.promotion_state[player]['menu_selection']}")
            
        if direction == 'left' and self.promotion_state[player]['menu_selection'] > 0:
            self.promotion_state[player]['menu_selection'] -= 1
            print(f"🎯 Player {player}: Promotion menu ← {self.promotion_options[self.promotion_state[player]['menu_selection']]}")
        elif direction == 'right' and self.promotion_state[player]['menu_selection'] < len(self.promotion_options) - 1:
            self.promotion_state[player]['menu_selection'] += 1
            print(f"🎯 Player {player}: Promotion menu → {self.promotion_options[self.promotion_state[player]['menu_selection']]}")
        else:
            print(f"🔥 PROMOTION NAV: No movement possible - at edge or invalid direction")
    
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
        
        print(f"🎉 Player {player}: Promoted {selected_piece.piece_id} to {promotion_choice} at {target_pos}")
        
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
