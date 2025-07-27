import queue
from typing import Dict, Tuple, Optional
from It1_interfaces.Command import Command
from It1_interfaces.ChessRulesValidator import ChessRulesValidator


class InputManager:
    """Manager for handling player input and piece selection."""
    
    def __init__(self, board, user_input_queue: queue.Queue):
        """Initialize the input manager."""
        self.board = board
        self.user_input_queue = user_input_queue
        self.chess_validator = ChessRulesValidator()
        self.selection = {
            'A': {'pos': [0, 0], 'selected': None, 'color': (255, 0, 0)},
            'B': {'pos': [7, 7], 'selected': None, 'color': (0, 0, 255)}
        }
    
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
                    now = game_time_ms_func()
                    cmd = Command.create_move_command(now, selected.piece_id, start_pos, pos)
                    self.user_input_queue.put(cmd)
            self.selection[player]['selected'] = None
    
    def get_selection(self, player: str) -> Dict:
        """Get the current selection for a player."""
        return self.selection[player]
    
    def get_all_selections(self) -> Dict:
        """Get all player selections."""
        return self.selection
