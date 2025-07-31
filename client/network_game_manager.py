"""
Network Game Mode - WebSocket Integration for Chess Game
Extends the existing game with multiplayer functionality.
"""

import sys
from pathlib import Path

# Add paths to components
base_path = Path(__file__).parent.parent
sys.path.append(str(base_path / "server" / "interfaces"))
sys.path.append(str(base_path / "client" / "interfaces"))
sys.path.append(str(base_path / "shared" / "interfaces"))

from Game import Game
from EventBus import EventBus
from EventTypes import MOVE_DONE, PIECE_CAPTURED, GAME_STARTED, GAME_ENDED, INVALID_MOVE
from websocket_client import ChessWebSocketClient
import threading
import time
import logging

logger = logging.getLogger(__name__)


class NetworkGameManager:
    """Manages network functionality for the chess game."""
    
    def __init__(self, game: Game, event_bus: EventBus):
        self.game = game
        self.event_bus = event_bus
        self.websocket_client = ChessWebSocketClient()
        self.is_network_game = False
        self.my_color = None  # Just for player identification
        self.last_state_time = 0  # For tracking state updates
        
        # Setup WebSocket event handlers
        self._setup_websocket_handlers()
        
        # Subscribe to game events - in real-time mode, we track everything
        self.event_bus.subscribe(MOVE_DONE, self)
        self.event_bus.subscribe(PIECE_CAPTURED, self)
        self.event_bus.subscribe("PIECE_SELECTED", self)
        self.event_bus.subscribe("PIECE_DESELECTED", self)
        self.event_bus.subscribe("PIECE_MOVING", self)  # Track piece movements
        self.event_bus.subscribe("RENDER_FRAME", self)  # For UI updates
        
        logger.info("Real-time Network Game Manager initialized")
    
    def _setup_websocket_handlers(self):
        """Setup WebSocket event handlers."""
        self.websocket_client.on_connected = self._on_connected
        self.websocket_client.on_disconnected = self._on_disconnected
        self.websocket_client.on_room_created = self._on_room_created
        self.websocket_client.on_room_joined = self._on_room_joined
        self.websocket_client.on_move_received = self._on_move_received
        self.websocket_client.on_player_joined = self._on_player_joined
        self.websocket_client.on_player_left = self._on_player_left
        self.websocket_client.on_game_state_received = self._on_game_state_received
        
        # Setup periodic game state sync
        self._sync_timer = 0
        self._sync_interval = 200  # Sync every 200ms for better consistency
        self.websocket_client.on_error = self._on_error
    
    def start_network_game(self, mode: str = "create", room_id: str = None):
        """Start a network game."""
        logger.info(f"Starting network game mode: {mode}")
        
        # Connect to server
        self.websocket_client.start_connection()
        
        # Wait for connection to establish
        max_wait = 50  # 5 seconds max
        wait_count = 0
        while not self.websocket_client.is_connected() and wait_count < max_wait:
            time.sleep(0.1)
            wait_count += 1
        
        if not self.websocket_client.is_connected():
            logger.error("Failed to connect to server")
            return False
        
        if mode == "create":
            self.websocket_client.create_room()
        elif mode == "join" and room_id:
            self.websocket_client.join_room(room_id)
        else:
            logger.error("Invalid network game mode")
            return False
        
        self.is_network_game = True
        return True
    
    def stop_network_game(self):
        """Stop network game and disconnect."""
        logger.info("Stopping network game")
        self.is_network_game = False
        self.websocket_client.stop_connection()
    
    def handle_event(self, event_type: str, data: dict):
        """Handle game events for network synchronization."""
        if event_type == "RENDER_FRAME":
            self.draw_room_info()
            return
            
        if not self.is_network_game:
            return
        
        # In real-time mode (Kung Fu Chess), we send all moves and captures immediately
        if event_type == MOVE_DONE:
            # Send move to other players
            command = data.get('command')
            if command and hasattr(command, 'params') and len(command.params) >= 2:
                from_pos = self._convert_position_to_notation(command.params[0])
                to_pos = self._convert_position_to_notation(command.params[1])
                piece = command.piece_id[:2] if command.piece_id else ''
                
                # Get piece and its details
                piece_obj = next((p for p in self.game.pieces.values() if p.piece_id.startswith(piece)), None)
                if piece_obj:
                    # Get complete state info
                    current_state = piece_obj.current_state
                    state_info = {
                        'name': current_state.current_state_name,
                        'is_rest': current_state.requires_rest_period,
                        'rest_duration': current_state.rest_period_duration_ms,
                        'activation_time': current_state.state_activation_timestamp,
                        'speed': current_state.physics.movement_speed,
                        'rest_remaining': max(0, current_state.rest_period_duration_ms - (self.game.game_time_ms() - current_state.state_activation_timestamp)),
                        'network_time': self.game.game_time_ms(),
                        'transitions': {}
                    }
                    
                    # Send move command with complete state info
                    self.websocket_client.make_move(
                        from_pos=from_pos,
                        to_pos=to_pos,
                        piece=piece,
                        state_info=state_info
                    )
                    
                    # Also apply the move locally so you see it immediately
                    from_pos_tuple = self._convert_notation_to_position(from_pos)
                    to_pos_tuple = self._convert_notation_to_position(to_pos)
                    
                    # Find and update the piece locally
                    for p in self.game.pieces.values():
                        current_pos = tuple(p.current_state.physics.current_board_cell)
                        if current_pos == from_pos_tuple:
                            p.current_state.physics.current_board_cell = list(to_pos_tuple)
                            p.current_state.physics.target_board_cell = list(to_pos_tuple)
                            p.current_state.physics.is_currently_moving = False
                            break
                    
                    print(f"📤 Applied your move: {from_pos} → {to_pos}")
                else:
                    logger.warning(f"Could not find piece {piece} to send move")
            else:
                logger.warning("Invalid move data received from game")
                
        elif event_type == PIECE_CAPTURED:
            # Send capture event
            captured_piece = data.get('piece')
            if captured_piece:
                piece_id = captured_piece.piece_id
                position = self._convert_position_to_notation(captured_piece.current_state.physics.current_board_cell)
                self.websocket_client.notify_piece_captured(piece_id, position)
                logger.info(f"Sent capture notification: {piece_id} at {position}")
                
        # Periodically sync full game state (less frequently)
        current_time = self.game.game_time_ms()
        if not hasattr(self, '_last_sync_time'):
            self._last_sync_time = 0
        if (current_time - self._last_sync_time > 100 and  # Sync more frequently (every 100ms)
            hasattr(self, 'room_id') and self.room_id):  # And only if in a room
            self._last_sync_time = current_time
            self._send_full_game_state()
    
    def _send_full_game_state(self):
        """Send complete game state to synchronize everything."""
        try:
            if not self.websocket_client.is_connected:
                logger.warning("Can't send state - not connected")
                return
                
            # Don't send state if we're not in a room or waiting for players
            if not hasattr(self, 'room_id') or not self.room_id:
                logger.warning("Can't send state - no room")
                return
                
            # Get all piece positions and states
            pieces_state = {}
            for piece_id, piece in self.game.pieces.items():
                # Get current cell coordinates
                curr_pos = piece.current_state.physics.current_board_cell
                target_pos = piece.current_state.physics.target_board_cell
                
                # Get command information for state sync
                command_type = 'move'
                command_params = []
                if piece.current_state.current_command:
                    command_type = piece.current_state.current_command.type
                    command_params = piece.current_state.current_command.params
                    
                # Get state machine info
                current_state = piece.current_state
                current_state_name = current_state.current_state_name
                transitions = {}  # לא נשתמש במעברי מצב
                last_transition_time = current_state.state_activation_timestamp

                pieces_state[piece_id] = {
                    'position': curr_pos,
                    'state': current_state_name,
                    'state_info': {
                        'name': current_state_name,
                        'transitions': transitions,
                        'last_transition_time': last_transition_time,
                        'activation_time': current_state.state_activation_timestamp,
                        'is_rest': current_state.requires_rest_period,
                        'rest_duration': current_state.rest_period_duration_ms,
                        'speed': current_state.physics.movement_speed
                    },
                    'is_moving': piece.current_state.physics.is_currently_moving,
                    'target_position': target_pos,
                    'last_update': self.game.game_time_ms(),
                    'command_type': command_type,
                    'command_params': command_params
                }
                logger.debug(f"Piece {piece_id} state: pos={curr_pos}, target={target_pos}, moving={piece.current_state.physics.is_currently_moving}")
            
            # Get player selections with full info
            selections = {}
            all_selections = self.game.input_manager.get_all_selections()
            for player, sel in all_selections.items():
                selections[player] = {
                    'pos': sel['pos'],
                    'selected_piece_id': sel['selected'].piece_id if sel['selected'] else None,
                    'last_update': self.game.game_time_ms()
                }
            
            # Get detailed game stats
            game_stats = {
                'game_time': self.game.game_time_ms(),
                'last_sync': self.game.game_time_ms()
            }
            
            # Add score if available
            if hasattr(self.game, 'score_manager'):
                game_stats['scores'] = self.game.score_manager.get_score()
            
            # Add move history if available
            if hasattr(self.game, 'move_logger'):
                game_stats['moves_log'] = {
                    'A': self.game.move_logger.get_recent_moves_for_player('A'),
                    'B': self.game.move_logger.get_recent_moves_for_player('B')
                }
            
            # Check each piece's state before sending
            for piece_id, piece_data in pieces_state.items():
                piece = self.game.pieces.get(piece_id)
                if piece and piece.current_state.requires_rest_period:
                    current_time = self.game.game_time_ms()
                    time_since_activation = current_time - piece.current_state.state_activation_timestamp
                    piece_data['is_resting'] = time_since_activation < piece.current_state.rest_period_duration_ms
                    piece_data['rest_remaining'] = max(0, piece.current_state.rest_period_duration_ms - time_since_activation)
            
            # Create complete state with timing info
            game_state = {
                'type': 'game_state',
                'state': {
                    'pieces': pieces_state,
                    'selections': selections,
                    'game_stats': game_stats,
                    'game_time': self.game.game_time_ms(),
                    'player': self.my_color,
                    'sync_time': self.game.game_time_ms(),
                    'room_id': self.room_id
                }
            }
            
            # Log state for debugging
            logger.debug(f"Sending game state update:")
            logger.debug(f"- Pieces: {len(pieces_state)} pieces")
            logger.debug(f"- Selections: {len(selections)} players")
            logger.debug(f"- Game time: {game_stats.get('game_time')}")
            
            self.websocket_client.send_message(game_state)
            
        except Exception as e:
            logger.error(f"Failed to send game state: {e}")
    
    # def _on_move_received(self, piece_info: dict):
    #     """Handle move received from other player."""
    #     try:
    #         if not self.is_network_game:
    #             return

    #         # לוג מפורט של המידע שהתקבל
    #         logger.info(f"Received piece_info: {piece_info}")
                
    #         # Get move info
    #         from_pos = self._convert_notation_to_position(piece_info.get('from', ''))
    #         to_pos = self._convert_notation_to_position(piece_info.get('to', ''))
    #         piece_id = piece_info.get('piece', '')
            
    #         # Get complete state info
    #         state_info = piece_info.get('state_info')
    #         if not state_info:
    #             # אם אין מידע על מצב, נחפש אותו מהחייל עצמו
    #             piece = next((p for p in self.game.pieces.values() if p.piece_id.startswith(piece_id)), None)
    #             if piece:
    #                 current_state = piece.current_state
    #                 state_info = {
    #                     'name': current_state.current_state_name,
    #                     'is_rest': current_state.requires_rest_period,
    #                     'rest_duration': current_state.rest_period_duration_ms,
    #                     'activation_time': current_state.state_activation_timestamp,
    #                     'speed': current_state.physics.movement_speed,
    #                     'network_time': piece_info.get('network_time', self.game.game_time_ms())
    #                 }
    #             else:
    #                 state_info = {
    #                     'name': 'idle',
    #                     'is_rest': False,
    #                     'rest_duration': 0,
    #                     'activation_time': self.game.game_time_ms(),
    #                     'speed': 1.0,
    #                     'network_time': self.game.game_time_ms()
    #                 }
            
    #         logger.info(f"Processing network move with state:")
    #         logger.info(f"  Piece: {piece_id}")
    #         logger.info(f"  From: {from_pos} → {to_pos}")
    #         logger.info(f"  State: {state_info['name']}")
    #         logger.info(f"  Rest: {state_info['is_rest']}")
    #         logger.info(f"  Rest Duration: {state_info['rest_duration']}ms")
            
    #         # Find matching piece
    #         piece = next((p for p in self.game.pieces.values() if p.piece_id.startswith(piece_id)), None)
    #         if not piece:
    #             logger.warning(f"No piece found matching {piece_id}")
    #             return
                
    #         # Check if piece is in rest period before doing anything
    #         if piece.current_state.requires_rest_period:
    #             current_time = self.game.game_time_ms()
    #             time_since_activation = current_time - piece.current_state.state_activation_timestamp
    #             if time_since_activation < piece.current_state.rest_period_duration_ms:
    #                 logger.warning(f"⚠️ Piece {piece_id} is in rest period, cannot move!")
    #                 print(f"⚠️ Cannot move piece {piece_id} - in rest period for {(piece.current_state.rest_period_duration_ms - time_since_activation)/1000:.1f}s more")
    #                 return
                
    #         # Create command and update state together
    #         from shared.interfaces.Command import Command
    #         current_time = self.game.game_time_ms()
            
    #         # Create a copy of the current state for comparison
    #         original_state = piece.current_state.create_independent_copy_of_state()
            
    #         # Create move command
    #         move_cmd = Command(current_time, piece.piece_id, "move", [from_pos, to_pos])
            
    #         # Get the next state from the state machine
    #         next_state = piece.current_state.get_state_after_command(move_cmd, current_time)
    #         if not next_state:
    #             next_state = piece.current_state.create_independent_copy_of_state()
            
    #         # Update the state properties on the new state
    #         next_state.current_state_name = state_info['name']
    #         next_state.requires_rest_period = state_info['is_rest']
    #         next_state.rest_period_duration_ms = state_info['rest_duration']
    #         next_state.state_activation_timestamp = state_info['activation_time']
    #         next_state.physics.movement_speed = state_info['speed']
    #         next_state.physics.current_board_cell = to_pos
    #         next_state.physics.target_board_cell = to_pos
    #         next_state.physics.is_currently_moving = True
            
    #         # Apply the new state to the piece
    #         piece.current_state = next_state
            
    #         # Let the state machine process the command and transitions
    #         new_state = piece.current_state.get_state_after_command(move_cmd, current_time)
    #         if new_state and new_state is not piece.current_state:
    #             # Keep the state properties we set
    #             new_state.current_state_name = state_info['name']
    #             new_state.requires_rest_period = state_info['is_rest']
    #             new_state.rest_period_duration_ms = state_info['rest_duration']
    #             new_state.state_activation_timestamp = state_info['activation_time']
    #             piece.current_state = new_state
                
    #         # Update transitions
    #         if 'transitions' in state_info:
    #             for event, target_state in state_info['transitions'].items():
    #                 target = piece.current_state.create_independent_copy_of_state()
    #                 target.current_state_name = target_state
    #                 piece.current_state.configure_state_transition_rule(event, target)
            
    #         logger.info(f"Updated piece {piece.piece_id} state:")
    #         logger.info(f"  From: {original_state.current_state_name} → {piece.current_state.current_state_name}")
    #         logger.info(f"  Rest Required: {piece.current_state.requires_rest_period}")
    #         logger.info(f"  Rest Duration: {piece.current_state.rest_period_duration_ms}ms")
    #         logger.info(f"  Position: {from_pos} → {to_pos}")
                
    #     except Exception as e:
    #         logger.error(f"Error handling network move: {e}", exc_info=True)
            
    #     except Exception as e:
    #         logger.error(f"Error handling network move: {e}")
            
    def _get_piece_pos(self, piece) -> tuple:
        """Get current position of a piece."""
        return piece.current_state.physics.current_board_cell if piece else None
        
    def _log_piece_update(self, piece_id: str, old_pos: tuple, new_pos: tuple, piece_data: dict):
        """Log detailed piece state updates."""
        logger.info(f"\n=== Piece {piece_id} Network Sync ===")
        if old_pos != new_pos:
            logger.info(f"Position: {old_pos} -> {new_pos}")
        if 'target_position' in piece_data:
            logger.info(f"Target Position: {piece_data['target_position']}")
        if 'is_moving' in piece_data:
            logger.info(f"Moving State: {piece_data['is_moving']}")
        if 'state' in piece_data:
            logger.info(f"Game State: {piece_data['state']}")
        logger.info("================================")

    def draw_room_info(self):
        """Display room information on the game board."""
        if not hasattr(self.game, 'graphics') or not self.room_id:
            return
            
        info_text = f"Room ID: {self.room_id}"
        # Draw text in white at the top-left corner
        try:
            from interfaces.GraphicsFactory import get_graphics_instance
            graphics = get_graphics_instance()
            graphics.draw_text(info_text, (10, 10), color=(255, 255, 255), size=24, bold=True)
        except Exception as e:
            logger.error(f"Failed to draw room info: {e}")
        
    def _apply_piece_state(self, piece, state_data: dict, current_time: int = None):
        """Apply received piece state to a piece using the state machine."""
        if not current_time:
            current_time = self.game.game_time_ms()

        # Store original state for logging
        original_state = piece.current_state.current_state_name

        # Get complete state information from data
        state_info = state_data.get('state_info', {})
        if not state_info and 'state' in state_data:  # Backwards compatibility
            state_info = {
                'name': state_data['state'],
                'activation_time': state_data.get('state_activation_time', current_time),
                'is_rest': False,
                'rest_duration': 0,
                'transitions': {}
            }

        # Check if piece is in rest period
        if state_data.get('is_resting', False):
            piece.current_state.requires_rest_period = True
            if 'rest_remaining' in state_data:
                network_time = state_data.get('network_time', self.game.game_time_ms())
                piece.current_state.state_activation_timestamp = network_time - (piece.current_state.rest_period_duration_ms - state_data['rest_remaining'])
            logger.info(f"Piece {piece.piece_id} is resting, keeping rest state")
            return

        # Get command information for state machine
        cmd_type = state_data.get('command_type', 'move')
        cmd_params = state_data.get('command_params', [])
            
        # Create command with state timing
        from shared.interfaces.Command import Command
        state_cmd = Command(state_info['activation_time'], piece.piece_id, cmd_type, cmd_params)
        
        # Use state machine to transition
        next_state = piece.current_state.get_state_after_command(state_cmd, current_time)
        if next_state:
            next_state.current_state_name = state_info['name']
            next_state.state_activation_timestamp = state_info['activation_time']
            if 'is_rest' in state_info:
                next_state.requires_rest_period = state_info['is_rest']
                next_state.rest_period_duration_ms = state_info.get('rest_duration', 0)
        
        if next_state is not piece.current_state:
            # Apply the new state
            piece.current_state = next_state
            logger.info(f"Updated piece {piece.piece_id} through state machine:")
            logger.info(f"  New State: {next_state.current_state_name}")
            logger.info(f"  Rest Required: {next_state.requires_rest_period}")
            logger.info(f"  Rest Duration: {next_state.rest_period_duration_ms}ms")
            logger.info(f"  Activation Time: {next_state.state_activation_timestamp}")
            
        # Also update the state according to normal state machine rules
        updated_state = next_state.update_state_and_check_for_transitions(current_time)
        if updated_state is not next_state:
            piece.current_state = updated_state
            logger.info(f"State machine auto-transition for {piece.piece_id}:")
            logger.info(f"  Final State: {updated_state.current_state_name}")
            
        # Handle capture state
        if piece.current_state.current_state_name == 'captured':
            self.event_bus.publish(PIECE_CAPTURED, {"piece": piece})
        if not state_data:
            return
            
        old_state = piece.current_state.current_state_name
        old_moving = piece.current_state.physics.is_currently_moving
            
        # Update piece state with time
        if 'state' in state_data:
            piece.current_state.current_state_name = state_data['state']
            if current_time:
                piece.current_state._state_start_time = current_time
            
        # Update movement state
        if 'is_moving' in state_data:
            piece.current_state.physics.is_currently_moving = state_data['is_moving']
            
        # Log state changes for debugging
        if 'state' in state_data and old_state != state_data['state']:
            logger.info(f"Piece {piece.piece_id} state changed: {old_state} -> {state_data['state']}")
            
        if 'is_moving' in state_data and old_moving != state_data['is_moving']:
            logger.info(f"Piece {piece.piece_id} movement changed: {old_moving} -> {state_data['is_moving']}")
            
    def _on_game_state_received(self, state_data: dict):
        """Apply received game state to synchronize everything."""
        try:
            # Check if data is wrapped in 'state' key (from server)
            if 'pieces' not in state_data and 'state' in state_data:
                state_data = state_data['state']
                
            player = state_data.get('player', 'unknown')
            sync_time = state_data.get('sync_time', 0)
            
            # Check if this is newer state than what we have
            if hasattr(self, '_last_sync_time') and sync_time <= self._last_sync_time:
                logger.debug(f"Ignoring older state update from {player}")
                return
                
            # Don't apply our own state
            if player == self.my_color:
                logger.debug("Ignoring own state update")
                return
                
            self._last_sync_time = sync_time
            logger.info(f"Applying state update from {player} at time {sync_time}")
                
            pieces_state = state_data.get('pieces', {})
            selections_state = state_data.get('selections', {})
            current_time = self.game.game_time_ms()
            
            logger.info(f"🔄 Syncing full game state from {player}")
            
            # Update all piece positions and states
            for piece_id, piece_data in pieces_state.items():
                if piece_id in self.game.pieces:
                    piece = self.game.pieces[piece_id]
                    
                    # Get current state before update
                    old_pos = piece.current_state.physics.current_board_cell
                    old_state = piece.current_state.current_state_name
                    
                    # Update position and state
                    new_pos = tuple(piece_data['position'])
                    
                # Update rest state first if needed
                state_info = piece_data.get('state_info', {})
                if state_info.get('is_rest', False):
                    piece.current_state.requires_rest_period = True
                    piece.current_state.rest_period_duration_ms = state_info.get('rest_duration', 0)
                    if 'rest_remaining' in piece_data:
                        network_time = piece_data.get('network_time', self.game.game_time_ms())
                        piece.current_state.state_activation_timestamp = network_time - (piece.current_state.rest_period_duration_ms - piece_data['rest_remaining'])
                    logger.info(f"Updated rest state for {piece_id}")
                
                # Apply complete state with timing
                self._apply_piece_state(piece, piece_data, current_time)
                
                # Update target position if moving
                if piece_data.get('is_moving', False):
                    target_pos = piece_data.get('target_position')
                    if target_pos:
                        piece.current_state.physics.target_board_cell = tuple(target_pos)                    # Log state changes
                    self._log_piece_update(piece_id, old_pos, new_pos, piece_data)
                    if old_state != piece.current_state.current_state_name:
                        logger.info(f"State changed: {old_state} → {piece.current_state.current_state_name}")
                    piece.current_state.physics.target_board_cell = tuple(piece_data['target_position'])
                    piece.current_state.physics.is_currently_moving = piece_data['is_moving']
                    
                    # Update board state if position changed
                    if old_pos != new_pos:
                        # Clear old position from board
                        if old_pos and old_pos in self.game.board.board_state:
                            self.game.board.board_state[old_pos] = None
                        
                        # Set new position on board
                        if new_pos:
                            self.game.board.board_state[new_pos] = piece
                    
                    # Update visual state
                    network_time = state_data.get('network_time', self.game.game_time_ms())
                    piece.current_state._state_start_time = network_time
                    # Update REST state
                    if state_info.get('is_rest', False):
                        piece.current_state.requires_rest_period = True
                        piece.current_state.rest_period_duration_ms = state_info.get('rest_duration', 0)
                        piece.current_state.state_activation_timestamp = state_info.get('activation_time', network_time)
                    
                    print(f"  🔧 Updated {piece_id}: {old_pos} -> {new_pos}")
            
            # Update selections (only show opponent's selection)
            opponent_player = 'A' if self.my_color == 'black' else 'B'
            if opponent_player in selections_state:
                opponent_selection = selections_state[opponent_player]
                
                # Update opponent's cursor position
                if hasattr(self.game.input_manager, '_player_positions'):
                    self.game.input_manager._player_positions[opponent_player] = tuple(opponent_selection['pos'])
                
                # Update opponent's selected piece
                selected_piece_id = opponent_selection.get('selected_piece_id')
                if selected_piece_id and selected_piece_id in self.game.pieces:
                    if hasattr(self.game.input_manager, '_player_selections'):
                        self.game.input_manager._player_selections[opponent_player] = self.game.pieces[selected_piece_id]
            
            # Update game stats
            game_stats = state_data.get('game_stats', {})
            if game_stats:
                # Update scores
                if 'scores' in game_stats and hasattr(self.game, 'score_manager'):
                    # Can't directly set scores, but we can log the sync
                    print(f"  📊 Received scores: {game_stats['scores']}")
                
                # Update moves log 
                if 'moves_log' in game_stats and hasattr(self.game, 'move_logger'):
                    # Can't directly set moves log, but we can log the sync
                    total_moves = len(game_stats['moves_log'].get('A', [])) + len(game_stats['moves_log'].get('B', []))
                    print(f"  📝 Received moves log with {total_moves} moves")
                
            print(f"✅ Game state synchronized")
            
        except Exception as e:
            logger.error(f"Failed to apply game state: {e}")
            import traceback
            traceback.print_exc()
    
    def update(self, event_type: str = None, data: dict = None):
        """Handle both EventBus events and regular updates."""
        # If called with parameters, handle as EventBus event
        if event_type is not None:
            self.handle_event(event_type, data or {})
        
        # Always update network state
        if self.is_network_game:
            self.websocket_client.process_incoming_messages()
            
            # Check if we need to sync state (only if there are other players)
            current_time = self.game.game_time_ms()
            if not hasattr(self, '_last_periodic_sync'):
                self._last_periodic_sync = 0
            # Only sync if enough time passed and we have room with other players
            if (current_time - self._last_periodic_sync > 500 and  # Less frequent sync
                hasattr(self, 'room_id') and self.room_id):
                self._last_periodic_sync = current_time
                self._send_full_game_state()
    
    def _convert_position_to_notation(self, pos: tuple) -> str:
        """Convert (row, col) position to chess notation (e.g., (0, 0) -> 'a8')."""
        if not isinstance(pos, (tuple, list)) or len(pos) != 2:
            return "a1"
        
        row, col = pos
        if not (0 <= row < 8 and 0 <= col < 8):
            return "a1"
        
        file = chr(ord('a') + col)
        rank = str(8 - row)
        return f"{file}{rank}"
    
    def _convert_notation_to_position(self, notation: str) -> tuple:
        """Convert chess notation to (row, col) position (e.g., 'a8' -> (0, 0))."""
        if not notation or len(notation) != 2:
            return (0, 0)
        
        try:
            file = notation[0].lower()
            rank = notation[1]
            
            col = ord(file) - ord('a')
            row = 8 - int(rank)
            
            if not (0 <= row < 8 and 0 <= col < 8):
                return (0, 0)
            
            return (row, col)
        except (ValueError, IndexError):
            return (0, 0)
    
    
    # WebSocket Event Handlers
    def _on_connected(self):
        """Called when connected to server."""
        logger.info("🌐 Connected to chess server!")
        print("🌐 Connected to chess server!")
    
    def _on_disconnected(self):
        """Called when disconnected from server."""
        logger.info("🔌 Disconnected from chess server")
        print("🔌 Disconnected from chess server")
        self.is_network_game = False
        self.room_id = None
        self.my_color = None
    
    def _on_room_created(self, room_id: str, player_color: str):
        """Called when room is created."""
        self.room_id = room_id
        self.my_color = player_color
        self.is_my_turn = (player_color == "white")
        
        # Update game's input manager with network settings
        if hasattr(self.game, 'input_manager'):
            self.game.input_manager.set_network_settings(
                is_network_game=True,
                my_player_color=player_color
            )
        
        logger.info(f"🎮 Room created! Room ID: {room_id}, Playing as: {player_color}")
        print(f"🎮 Room created!")
        print(f"📋 Room ID: {room_id}")
        print(f"⚪ You are playing as: {player_color}")
        print("👥 Waiting for opponent to join...")
    
    def _on_room_joined(self, room_id: str, player_color: str):
        """Called when joined a room."""
        self.room_id = room_id
        self.my_color = player_color
        
        # Update game's input manager with network settings
        if hasattr(self.game, 'input_manager'):
            self.game.input_manager.set_network_settings(
                is_network_game=True,
                my_player_color=player_color
            )
        
        if player_color == "spectator":
            logger.info(f"👁️ Joined room {room_id} as spectator")
            print(f"👁️ Joined room {room_id} as spectator")
        else:
            self.is_my_turn = (player_color == "white")
            logger.info(f"🎮 Joined room {room_id} as {player_color}")
            print(f"🎮 Joined room {room_id}!")
            print(f"⚪ You are playing as: {player_color}")
    
    # def _on_move_received(self, move_data: dict):
    #     """Called when a move is received from opponent."""
    #     from_notation = move_data.get('from', 'a1')
    #     to_notation = move_data.get('to', 'a1')
    #     player = move_data.get('player', 'unknown')
        
    #     # Don't process our own moves
    #     if player == self.my_color:
    #         print(f"🔄 Skipping own move: {from_notation} → {to_notation}")
    #         return
        
    #     from_pos = self._convert_notation_to_position(from_notation)
    #     to_pos = self._convert_notation_to_position(to_notation)
        
    #     logger.info(f"📥 Received opponent move: {from_notation} to {to_notation}")
    #     print(f"📥 Opponent moved: {from_notation} → {to_notation} (from {from_pos} to {to_pos})")
        
    #     # Apply the move to our game board
    #     try:
    #         # Debug: Check if we have access to pieces
    #         if hasattr(self.game, 'pieces'):
    #             pieces_dict = self.game.pieces
    #             print(f"🔍 Found {len(pieces_dict)} pieces in game.pieces")
    #         elif hasattr(self.game, 'board') and hasattr(self.game.board, 'pieces'):
    #             pieces_dict = {piece.piece_id: piece for piece in self.game.board.pieces}
    #             print(f"🔍 Found {len(pieces_dict)} pieces in game.board.pieces")
    #         else:
    #             print(f"❌ Could not find pieces in game object")
    #             return
            
    #         # Find the piece at the source position
    #         piece_to_move = None
    #         print(f"🔍 Looking for piece at position {from_pos}...")
            
    #         for piece_id, piece in pieces_dict.items():
    #             current_pos = piece.current_state.physics.current_board_cell
    #             print(f"   Piece {piece_id} at {current_pos}")
    #             if current_pos == from_pos:
    #                 piece_to_move = piece
    #                 print(f"✅ Found piece to move: {piece_id}")
                    
    #                 # Check piece state before moving
    #                 if piece.current_state.requires_rest_period:
    #                     current_time = self.game.game_time_ms()
    #                     time_since_activation = current_time - piece.current_state.state_activation_timestamp
    #                     if time_since_activation < piece.current_state.rest_period_duration_ms:
    #                         logger.warning(f"⚠️ Piece {piece_id} is in rest period, cannot move!")
    #                         print(f"⚠️ Cannot move piece {piece_id} - in rest period for {(piece.current_state.rest_period_duration_ms - time_since_activation)/1000:.1f}s more")
    #                         return
    #                 break
            
    #         if piece_to_move:
    #             # Update the piece's physics position directly
    #             old_pos = piece_to_move.current_state.physics.current_board_cell
    #             piece_to_move.current_state.physics.current_board_cell = to_pos
    #             piece_to_move.current_state.physics.target_board_cell = to_pos
    #             piece_to_move.current_state.physics.is_currently_moving = False
                
    #             print(f"✅ Moved {piece_to_move.piece_id}: {old_pos} → {to_pos}")
    #             logger.info(f"✅ Applied opponent move: {piece_to_move.piece_id} to {to_pos}")
                
    #             # Force the piece to refresh its visual state
    #             piece_to_move.current_state._state_start_time = self.game.game_time_ms()
                
    #             print(f"🎨 Visual update forced for piece at {to_pos}")
                
    #         else:
    #             print(f"⚠️ No piece found at {from_pos}")
    #             logger.warning(f"⚠️ No piece found at {from_pos}")
            
    #         # Update turn
    #         self.is_my_turn = (player != self.my_color)
    #         print(f"🔄 Turn updated: is_my_turn = {self.is_my_turn}")
            
    #     except Exception as e:
    #         logger.error(f"❌ Failed to apply opponent move: {e}")
    #         print(f"❌ Error applying move: {e}")
    #         import traceback
    #         traceback.print_exc()
    
    def _on_move_received(self, move_data: dict):
        """Called when a move is received from opponent."""
        from_notation = move_data.get('from', 'a1')
        to_notation = move_data.get('to', 'a1')
        player = move_data.get('player', 'unknown')
        
        # Don't process our own moves (shouldn't happen now)
        if player == self.my_color:
            return
        
        from_pos = self._convert_notation_to_position(from_notation)
        to_pos = self._convert_notation_to_position(to_notation)
        
        print(f"📥 Opponent moved: {from_notation} → {to_notation}")
        
        # Apply the move to our game board
        try:
            # Find the piece at the source position
            piece_to_move = None
            for piece in self.game.pieces.values():
                current_pos = tuple(piece.current_state.physics.current_board_cell)
                if current_pos == from_pos:
                    piece_to_move = piece
                    break
            
            if piece_to_move:
                # Update the piece's position directly
                piece_to_move.current_state.physics.current_board_cell = list(to_pos)
                piece_to_move.current_state.physics.target_board_cell = list(to_pos)
                piece_to_move.current_state.physics.is_currently_moving = False
                
                print(f"✅ Applied opponent move: {piece_to_move.piece_id} to {to_pos}")
            else:
                print(f"⚠️ No piece found at {from_pos}")
            
        except Exception as e:
            logger.error(f"❌ Failed to apply opponent move: {e}")
            print(f"❌ Error applying move: {e}")

    def _on_player_joined(self, data: dict):
        """Called when a player joins the room."""
        players_count = data.get('players_count', 0)
        logger.info(f"👥 Player joined! Players in room: {players_count}")
        
        if players_count == 2:
            print("✅ Opponent joined! Game can begin!")
            print("🎯 Your turn!" if self.is_my_turn else " Wait for opponent's move")
        else:
            print(f"👥 Player joined (Total: {players_count}/2)")
    
    def _on_player_left(self, data: dict):
        """Called when a player leaves the room."""
        players_count = data.get('players_count', 0)
        logger.info(f"👋 Player left! Players in room: {players_count}")
        print(f"👋 Player left the game (Remaining: {players_count})")
        
        if players_count < 2:
            print("⏳ Waiting for opponent to join...")
    
    def _on_error(self, error_message: str):
        """Called when there's an error."""
        logger.error(f"❌ Network error: {error_message}")
        print(f"❌ Network error: {error_message}")
    
    def get_network_status(self) -> dict:
        """Get current network game status for real-time game."""
        return {
            'is_network_game': self.is_network_game,
            'connected': self.websocket_client.is_connected(),
            'room_info': self.websocket_client.get_room_info(),
            'my_color': self.my_color,
            'mode': 'real-time',  # Always real-time for Kung Fu Chess
            'last_sync': getattr(self, 'last_state_time', 0)
        }
