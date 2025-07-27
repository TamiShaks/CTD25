import queue
import threading
import pygame
import time
from typing import Dict, Tuple, Optional
from It1_interfaces.Command import Command
from It1_interfaces.ChessRulesValidator import ChessRulesValidator


class ThreadedInputManager(threading.Thread):
    """Threaded input manager that runs parallel to the game and listens for input."""
    
    def __init__(self, board, user_input_queue: queue.Queue, debug=False):
        """Initialize the threaded input manager."""
        super().__init__(daemon=True)  # Daemon thread - dies when main program exits
        self.board = board
        self.user_input_queue = user_input_queue
        self.chess_validator = ChessRulesValidator()
        self.debug = debug  # Control debug output
        self.selection = {
            'A': {'pos': [0, 0], 'selected': None, 'color': (255, 0, 0)},
            'B': {'pos': [7, 7], 'selected': None, 'color': (0, 0, 255)}
        }
        
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
        
    def run(self):
        """Main thread loop - listens for input continuously using key polling."""
        print("🎮 Input thread started - listening for player input...")
        
        while self._running:
            try:
                current_time = time.time()
                keys = pygame.key.get_pressed()
                
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
                if self.debug:
                    print(f"⚠️ Same position - deselecting {selected.piece_id}")
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
                    now = self._game_time_func()
                    cmd = Command.create_move_command(now, selected.piece_id, start_pos, pos)
                    self.user_input_queue.put(cmd)
                    print(f"✅ Player {player}: {selected.piece_id} {start_pos} → {pos}")  # Always show successful moves
                else:
                    if self.debug:
                        print(f"❌ Invalid chess rule: {selected.piece_id} {start_pos} → {pos}")
            else:
                if self.debug:
                    print(f"⚠️ Not a valid move: {selected.piece_id} {start_pos} → {pos}")
            self.selection[player]['selected'] = None
    
    def get_selection(self, player: str) -> Dict:
        """Get the current selection for a player."""
        return self.selection[player]
    
    def get_all_selections(self) -> Dict:
        """Get all player selections."""
        return self.selection
