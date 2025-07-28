import queue
from typing import Dict, Tuple, Optional
from It1_interfaces.Command import Command
from It1_interfaces.ChessRulesValidator import ChessRulesValidator
from It1_interfaces.EventTypes import INVALID_MOVE, PAWN_PROMOTION


class InputManager:
    """Manager for handling player input and piece selection."""
    
    def __init__(self, board, user_input_queue: queue.Queue, event_bus=None):
        """Initialize the input manager."""
        self.board = board
        self.user_input_queue = user_input_queue
        self.event_bus = event_bus
        self.chess_validator = ChessRulesValidator()
        self.selection = {
            'A': {'pos': [0, 0], 'selected': None, 'color': (255, 0, 0)},
            'B': {'pos': [7, 7], 'selected': None, 'color': (0, 0, 255)}
        }
        # Promotion state tracking
        self.promotion_state = {
            'A': {'active': False, 'piece': None, 'target_pos': None, 'menu_selection': 0},
            'B': {'active': False, 'piece': None, 'target_pos': None, 'menu_selection': 0}
        }
        self.promotion_options = ["Q", "R", "B", "N"]  # Queen, Rook, Bishop, Knight
    
    def move_selection(self, player: str, direction: str):
        """Move the selection cursor for the given player."""
        pos = self.selection[player]['pos']

        if direction == 'up' and pos[0] > 0:
            pos[0] -= 1
        elif direction == 'down' and pos[0] < self.board.H_cells - 1:
            pos[0] += 1
        elif direction == 'left' and pos[1] > 0:
            pos[1] -= 1
        elif direction == 'right' and pos[1] < self.board.W_cells - 1:
            pos[1] += 1

    def select_piece(self, player: str, pieces: Dict, game_time_ms_func):
        """Select or move a piece for the given player."""
        pos = tuple(self.selection[player]['pos'])
        selected = self.selection[player]['selected']
        player_color = "White" if player == "A" else "Black"

        if selected is None:
            # First keypress: select a piece at the cursor that belongs to this player
            for piece in pieces.values():
                p_pos = tuple(piece.current_state.physics.current_cell)
                if p_pos == pos and hasattr(piece, 'color') and piece.color == player_color:
                    self.selection[player]['selected'] = piece
                    break
        else:
            # Second keypress: try to move selected piece to cursor position
            start_pos = tuple(selected.current_state.physics.current_cell)
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
                for piece in pieces.values():
                    if tuple(piece.current_state.physics.current_cell) == pos:
                        target_piece = piece
                        break
                
                # Use chess validator to check all rules
                if self.chess_validator.is_valid_move(selected, start_pos, pos, target_piece, pieces):
                    # Check if this is a pawn promotion
                    if self.chess_validator.is_pawn_promotion(selected, pos):
                        # Start promotion process
                        self.promotion_state[player]['active'] = True
                        self.promotion_state[player]['piece'] = selected
                        self.promotion_state[player]['target_pos'] = pos
                        self.promotion_state[player]['menu_selection'] = 0
                        
                        # Publish promotion event to show popup
                        if self.event_bus:
                            self.event_bus.publish(PAWN_PROMOTION, {
                                "player": player,
                                "piece_id": selected.piece_id,
                                "from_pos": start_pos,
                                "to_pos": pos,
                                "options": self.promotion_options
                            })
                    else:
                        # Regular move
                        now = game_time_ms_func()
                        cmd = Command.create_move_command(now, selected.piece_id, start_pos, pos)
                        self.user_input_queue.put(cmd)
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
            self.selection[player]['selected'] = None
    
    def handle_promotion_navigation(self, player: str, direction: str):
        """Handle navigation in promotion menu."""
        if not self.promotion_state[player]['active']:
            return
            
        if direction == 'left' and self.promotion_state[player]['menu_selection'] > 0:
            self.promotion_state[player]['menu_selection'] -= 1
        elif direction == 'right' and self.promotion_state[player]['menu_selection'] < len(self.promotion_options) - 1:
            self.promotion_state[player]['menu_selection'] += 1
    
    def confirm_promotion(self, player: str, game_time_ms_func):
        """Confirm promotion choice and execute the move."""
        if not self.promotion_state[player]['active']:
            return
            
        selected_piece = self.promotion_state[player]['piece']
        target_pos = self.promotion_state[player]['target_pos']
        start_pos = tuple(selected_piece.current_state.physics.current_cell)
        promotion_choice = self.promotion_options[self.promotion_state[player]['menu_selection']]
        
        # Create promotion command
        now = game_time_ms_func()
        cmd = Command.create_promotion_command(now, selected_piece.piece_id, start_pos, target_pos, promotion_choice)
        self.user_input_queue.put(cmd)
        
        # Reset promotion state
        self.promotion_state[player]['active'] = False
        self.promotion_state[player]['piece'] = None
        self.promotion_state[player]['target_pos'] = None
        self.promotion_state[player]['menu_selection'] = 0
    
    def cancel_promotion(self, player: str):
        """Cancel promotion and return to normal play."""
        self.promotion_state[player]['active'] = False
        self.promotion_state[player]['piece'] = None
        self.promotion_state[player]['target_pos'] = None
        self.promotion_state[player]['menu_selection'] = 0
    
    def is_promotion_active(self, player: str) -> bool:
        """Check if promotion menu is active for player."""
        return self.promotion_state[player]['active']
    
    def get_promotion_state(self, player: str) -> Dict:
        """Get current promotion state for player."""
        return self.promotion_state[player]
    
    def get_selection(self, player: str) -> Dict:
        """Get the current selection for a player."""
        return self.selection[player]
    
    def get_all_selections(self) -> Dict:
        """Get all player selections."""
        return self.selection
