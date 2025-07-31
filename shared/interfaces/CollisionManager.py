"""
CollisionManager - Manages piece collisions and captures
Handles all logic related to piece collisions, captures, and movement blocking
"""
from typing import Dict, List
from Piece import Piece
from Command import Command

class CollisionManager:
    def __init__(self, event_bus=None):
        self.event_bus = event_bus

    def group_pieces_by_position(self, pieces: Dict[str, Piece], get_time_func) -> Dict[tuple, List[Piece]]:
        """Group all pieces by their current position."""
        positions: Dict[tuple, List[Piece]] = {}
        now = get_time_func()

        for piece in pieces.values():
            pos = piece.current_state.physics.get_current_pixel_position(now)
            if pos not in positions:
                positions[pos] = []
            positions[pos].append(piece)
        
        return positions

    def resolve_cell_collision(self, pieces: List[Piece], captured_pieces: List[Piece]):
        """Resolve collision between pieces in a single cell."""
        pieces_by_color = {
            "White": [p for p in pieces if p.color == "White"],
            "Black": [p for p in pieces if p.color == "Black"]
        }
        
        # Handle same-color collisions
        for color_group in pieces_by_color.values():
            if len(color_group) > 1:
                self.handle_friendly_collision(color_group)
        
        # Handle different-color collisions
        if pieces_by_color["White"] and pieces_by_color["Black"]:
            self.handle_enemy_collision(pieces, captured_pieces)

    def handle_friendly_collision(self, same_color_pieces):
        """Handle collision between pieces of the same color."""
        # Keep stationary pieces, block moving pieces
        stationary_pieces = [p for p in same_color_pieces if not p.current_state.physics.is_moving and p.current_state.state not in ["move", "jump"]]
        moving_pieces = [p for p in same_color_pieces if p.current_state.physics.is_moving or p.current_state.state in ["move", "jump"]]
        
        if stationary_pieces and moving_pieces:
            # Block moving pieces
            for moving_piece in moving_pieces:
                self.block_piece_movement(moving_piece)
        elif len(same_color_pieces) > 1:
            # Block all but the first piece
            for p in same_color_pieces[1:]:
                self.block_piece_movement(p)

    def block_piece_movement(self, piece, get_time_func=None):
        """Block a piece's movement and return it to idle."""
        piece.current_state.physics.target_cell = piece.current_state.physics.current_cell
        piece.current_state.physics.is_moving = False
        if get_time_func:
            now = get_time_func()
            idle_cmd = Command(timestamp=now, piece_id=piece.piece_id, type="idle", params=[])
            piece.handle_command(idle_cmd, now)

    def handle_enemy_collision(self, pieces_in_cell, to_remove):
        """Handle collision between pieces of different colors."""
        # Find attacker (moving piece) vs defender (stationary piece)
        attacking_piece = None
        defending_piece = None
        
        for piece in pieces_in_cell:
            if (piece.current_state.physics.is_moving or 
                piece.current_state.state in ["move", "jump"]):
                attacking_piece = piece
            else:
                defending_piece = piece
        
        # If unclear, use most recent action time
        if not attacking_piece and len(pieces_in_cell) >= 2:
            if hasattr(pieces_in_cell[0], 'cooldown_system'):
                attacking_piece = max(pieces_in_cell, key=lambda p: getattr(p.cooldown_system, 'last_action_time', 0))
                defending_piece = min(pieces_in_cell, key=lambda p: getattr(p.cooldown_system, 'last_action_time', 0))
            else:
                attacking_piece, defending_piece = pieces_in_cell[0], pieces_in_cell[1]
        
        # Remove the defender
        if defending_piece and attacking_piece != defending_piece:
            to_remove.append(defending_piece)

    def remove_captured_pieces(self, pieces_dict: Dict[str, Piece], captured_pieces: List[Piece]):
        """Remove captured pieces and notify event bus."""
        for piece in captured_pieces:
            if self.event_bus:
                self.event_bus.publish("PIECE_CAPTURED", {"piece": piece})
            del pieces_dict[piece.piece_id]

    def resolve_collisions(self, pieces_dict: Dict[str, Piece], get_time_func):
        """Resolve piece collisions and captures based on chess-like rules."""
        piece_positions = self.group_pieces_by_position(pieces_dict, get_time_func)
        captured_pieces = []

        for pieces_in_cell in piece_positions.values():
            if len(pieces_in_cell) > 1:
                self.resolve_cell_collision(pieces_in_cell, captured_pieces)

        self.remove_captured_pieces(pieces_dict, captured_pieces)
