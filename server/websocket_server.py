"""
WebSocket Chess Server
Manages multiplayer chess games and client connections.
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime
from typing import Dict, Set, Optional, List
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ChessGameRoom:
    """Represents a real-time chess game room with two players."""
    
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.players: List[websockets.WebSocketServerProtocol] = []
        self.spectators: Set[websockets.WebSocketServerProtocol] = set()
        self.game_state = {
            'board': self._initialize_board(),
            'moves_history': [],
            'game_status': 'waiting',  # waiting, active, finished
            'winner': None,
            'last_update': datetime.now().timestamp()
        }
        self.created_at = datetime.now()
    
    def _initialize_board(self):
        """Initialize standard chess board position."""
        return {
            'a8': 'rb', 'b8': 'nb', 'c8': 'bb', 'd8': 'qb', 'e8': 'kb', 'f8': 'bb', 'g8': 'nb', 'h8': 'rb',
            'a7': 'pb', 'b7': 'pb', 'c7': 'pb', 'd7': 'pb', 'e7': 'pb', 'f7': 'pb', 'g7': 'pb', 'h7': 'pb',
            'a2': 'pw', 'b2': 'pw', 'c2': 'pw', 'd2': 'pw', 'e2': 'pw', 'f2': 'pw', 'g2': 'pw', 'h2': 'pw',
            'a1': 'rw', 'b1': 'nw', 'c1': 'bw', 'd1': 'qw', 'e1': 'kw', 'f1': 'bw', 'g1': 'nw', 'h1': 'rw'
        }
        
    def update_game_state(self, state_data: dict):
        """Update game state from client data."""
        if not state_data:
            return
            
        # Update piece positions and states
        if 'pieces' in state_data:
            self.game_state['pieces'] = state_data['pieces']
            
        # Update selections
        if 'selections' in state_data:
            self.game_state['selections'] = state_data['selections']
            
        # Update game stats
        if 'game_stats' in state_data:
            self.game_state['stats'] = state_data['game_stats']
            
        # Update game time
        if 'game_time' in state_data:
            self.game_state['time'] = state_data['game_time']
    
    def add_player(self, websocket: websockets.WebSocketServerProtocol) -> bool:
        """Add a player to the room. Returns True if successful, False if room is full."""
        if len(self.players) < 2:
            self.players.append(websocket)
            if len(self.players) == 2:
                self.game_state['game_status'] = 'active'
            return True
        return False
    
    def remove_player(self, websocket: websockets.WebSocketServerProtocol):
        """Remove a player from the room."""
        if websocket in self.players:
            self.players.remove(websocket)
            if len(self.players) < 2:
                self.game_state['game_status'] = 'waiting'
    
    def add_spectator(self, websocket: websockets.WebSocketServerProtocol):
        """Add a spectator to the room."""
        self.spectators.add(websocket)
    
    def remove_spectator(self, websocket: websockets.WebSocketServerProtocol):
        """Remove a spectator from the room."""
        self.spectators.discard(websocket)
    
    def get_player_color(self, websocket: websockets.WebSocketServerProtocol) -> Optional[str]:
        """Get the color assigned to a player."""
        if websocket in self.players:
            return 'white' if self.players.index(websocket) == 0 else 'black'
        return None
    
    async def broadcast_to_room(self, message: dict, exclude: Optional[websockets.WebSocketServerProtocol] = None):
        """Broadcast a message to all players and spectators in the room."""
        all_clients = set(self.players) | self.spectators
        if exclude:
            all_clients.discard(exclude)
        
        # Add server timestamp to message
        message['server_timestamp'] = datetime.now().timestamp()
        message_str = json.dumps(message)
        disconnected = []
        
        for client in all_clients:
            try:
                await client.send(message_str)
                if 'state' in message:  # Log state syncs for debugging
                    logger.debug(f"State sync sent to {client.remote_address}")
            except websockets.exceptions.ConnectionClosed:
                disconnected.append(client)
                logger.warning(f"Client disconnected during broadcast: {client.remote_address}")
        
        # Clean up disconnected clients
        for client in disconnected:
            self.remove_player(client)
            self.remove_spectator(client)
            logger.info(f"Cleaned up disconnected client: {client.remote_address}")


class ChessWebSocketServer:
    """Main WebSocket server for chess games."""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.rooms: Dict[str, ChessGameRoom] = {}
        self.client_rooms: Dict[websockets.WebSocketServerProtocol, str] = {}
        logger.info(f"Chess WebSocket Server initialized on {host}:{port}")
    
    async def register_client(self, websocket, path=None):
        """Handle client registration and message routing."""
        try:
            logger.info(f"Client connected from {websocket.remote_address}")
            await self.send_message(websocket, {
                'type': 'connection_established',
                'message': 'Connected to Chess Server',
                'server_time': datetime.now().isoformat()
            })
            
            async for message in websocket:
                await self.handle_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {websocket.remote_address} disconnected")
        except Exception as e:
            logger.error(f"Error handling client {websocket.remote_address}: {e}")
        finally:
            await self.cleanup_client(websocket)
    
    async def handle_message(self, websocket: websockets.WebSocketServerProtocol, message: str):
        """Handle incoming message from client."""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            # Only log important messages, not game_state spam
            if message_type != 'game_state':
                logger.info(f"Received message: {message_type} from {websocket.remote_address}")
            
            if message_type == 'create_room':
                await self.handle_create_room(websocket, data)
            elif message_type == 'join_room':
                await self.handle_join_room(websocket, data)
            elif message_type == 'list_rooms':
                await self.handle_list_rooms(websocket)
            elif message_type == 'make_move':
                await self.handle_make_move(websocket, data)
            elif message_type == 'piece_captured':
                await self.handle_piece_captured(websocket, data)
            elif message_type == 'game_state':
                await self.handle_game_state(websocket, data)
            elif message_type == 'chat_message':
                await self.handle_chat_message(websocket, data)
            elif message_type == 'ping':
                await self.send_message(websocket, {'type': 'pong', 'timestamp': datetime.now().isoformat()})
            else:
                await self.send_message(websocket, {
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                })
                
        except json.JSONDecodeError:
            await self.send_message(websocket, {
                'type': 'error',
                'message': 'Invalid JSON format'
            })
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self.send_message(websocket, {
                'type': 'error',
                'message': 'Internal server error'
            })
    
    async def handle_create_room(self, websocket: websockets.WebSocketServerProtocol, data: dict):
        """Handle room creation request."""
        room_id = str(uuid.uuid4())[:8]  # Short unique ID
        room = ChessGameRoom(room_id)
        
        # Add creator as first player
        room.add_player(websocket)
        self.rooms[room_id] = room
        self.client_rooms[websocket] = room_id
        
        await self.send_message(websocket, {
            'type': 'room_created',
            'room_id': room_id,
            'player_color': 'white',
            'game_state': room.game_state
        })
        
        logger.info(f"Room {room_id} created by {websocket.remote_address}")
        logger.info(f"🎮 Room {room_id}: 1/2 players connected (waiting for opponent)")
    
    async def handle_join_room(self, websocket: websockets.WebSocketServerProtocol, data: dict):
        """Handle room join request."""
        room_id = data.get('room_id')
        
        if room_id not in self.rooms:
            await self.send_message(websocket, {
                'type': 'error',
                'message': 'Room not found'
            })
            return
        
        room = self.rooms[room_id]
        
        # Try to add as player first
        if room.add_player(websocket):
            self.client_rooms[websocket] = room_id
            player_color = room.get_player_color(websocket)
            
            await self.send_message(websocket, {
                'type': 'room_joined',
                'room_id': room_id,
                'player_color': player_color,
                'game_state': room.game_state
            })
            
            # Notify other players
            await room.broadcast_to_room({
                'type': 'player_joined',
                'room_id': room_id,
                'players_count': len(room.players),
                'game_state': room.game_state
            }, exclude=websocket)
            
            logger.info(f"Player joined room {room_id} as {player_color}")
            logger.info(f"🎮 Room {room_id}: {len(room.players)}/2 players connected")
            
            if len(room.players) == 2:
                logger.info(f"🎯 Room {room_id}: GAME READY! Both players connected")
            
        else:
            # Add as spectator
            room.add_spectator(websocket)
            self.client_rooms[websocket] = room_id
            
            await self.send_message(websocket, {
                'type': 'room_joined',
                'room_id': room_id,
                'player_color': 'spectator',
                'game_state': room.game_state
            })
            
            logger.info(f"Spectator joined room {room_id}")
    
    async def handle_list_rooms(self, websocket: websockets.WebSocketServerProtocol):
        """Handle request for available rooms."""
        rooms_info = []
        for room_id, room in self.rooms.items():
            rooms_info.append({
                'room_id': room_id,
                'players_count': len(room.players),
                'spectators_count': len(room.spectators),
                'game_status': room.game_state['game_status'],
                'created_at': room.created_at.isoformat()
            })
        
        await self.send_message(websocket, {
            'type': 'rooms_list',
            'rooms': rooms_info
        })
    
    async def handle_make_move(self, websocket: websockets.WebSocketServerProtocol, data: dict):
        """Handle chess move from client."""
        room_id = self.client_rooms.get(websocket)
        if not room_id or room_id not in self.rooms:
            await self.send_message(websocket, {
                'type': 'error',
                'message': 'Not in a room'
            })
            return
        
        room = self.rooms[room_id]
        player_color = room.get_player_color(websocket)
        
        if not player_color:
            await self.send_message(websocket, {
                'type': 'error',
                'message': 'Only players can make moves'
            })
            return
        
        # Check if game has enough players
        if len(room.players) < 2:
            await self.send_message(websocket, {
                'type': 'error', 
                'message': 'Waiting for opponent to join'
            })
            return
        
        # Real-time mode: No turn checks needed
        
        # Get complete state info from client
        state_info = data.get('state_info', {
            'name': 'moving',
            'speed': 1.0,
            'is_rest': False,
            'rest_duration': 0,
            'activation_time': datetime.now().timestamp(),
            'transitions': {}
        })
        
        # Create piece info with state
        piece_info = {
            'from': data.get('from'),
            'to': data.get('to'),
            'piece': data.get('piece'),
            'timestamp': datetime.now().timestamp(),
            'state_info': state_info,
            'player': player_color
        }
        
        # Store move in history with state
        room.game_state['moves_history'].append(piece_info)
        
        # Update board and state tracking
        if 'board' not in room.game_state:
            room.game_state['board'] = {}
        if 'piece_states' not in room.game_state:
            room.game_state['piece_states'] = {}
            
        # Update board position
        room.game_state['board'][piece_info['to']] = piece_info['piece']
        # Track piece state
        room.game_state['piece_states'][piece_info['piece']] = state_info
        
        # Log detailed move info
        logger.info(f"Broadcasting move with state:")
        logger.info(f"  Piece: {piece_info['piece']}")
        logger.info(f"  From: {piece_info['from']} → {piece_info['to']}")
        logger.info(f"  State: {state_info['name']}")
        logger.info(f"  Rest: {state_info['is_rest']}")
        logger.info(f"  Rest Duration: {state_info['rest_duration']}ms")
        
        # Broadcast move to other players only (not back to sender)
        await room.broadcast_to_room({
            'type': 'move_made',
            'piece': piece_info,
            'timestamp': datetime.now().isoformat()
        }, exclude=websocket)
        
        logger.info(f"Move made in room {room_id}: {piece_info['from']} to {piece_info['to']}")
    
    async def handle_game_state(self, websocket: websockets.WebSocketServerProtocol, data: dict):
        """Handle real-time game state broadcast from client."""
        room_id = self.client_rooms.get(websocket)
        if not room_id or room_id not in self.rooms:
            return
        
        room = self.rooms[room_id]
        if len(room.players) < 2:
            return  # No broadcast needed if playing alone
        
        state_data = data.get('state', {})
        if not state_data:
            return
            
        # Update server's game state
        room.update_game_state(state_data)
        
        # Add timestamp to state
        state_data['timestamp'] = datetime.now().timestamp()
        state_data['from_player'] = room.get_player_color(websocket)
        
        # Broadcast to other players immediately (real-time game)
        await room.broadcast_to_room({
            'type': 'game_state',
            'state': state_data
        }, exclude=websocket)  # Don't send back to sender
        
        logger.debug(f"Real-time state update in room {room_id} from {state_data['from_player']}")
    
    async def handle_chat_message(self, websocket: websockets.WebSocketServerProtocol, data: dict):
        """Handle chat message from client."""
        room_id = self.client_rooms.get(websocket)
        if not room_id or room_id not in self.rooms:
            return
        
        room = self.rooms[room_id]
        player_color = room.get_player_color(websocket) or 'spectator'
        
        chat_message = {
            'type': 'chat_message',
            'player': player_color,
            'message': data.get('message', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        await room.broadcast_to_room(chat_message)
    
    async def handle_piece_captured(self, websocket: websockets.WebSocketServerProtocol, data: dict):
        """Handle piece capture notification."""
        room_id = self.client_rooms.get(websocket)
        if not room_id or room_id not in self.rooms:
            return
            
        room = self.rooms[room_id]
        capture_data = data.get('piece', {})
        piece_id = capture_data.get('id')
        position = capture_data.get('position')
        
        if not piece_id or not position:
            return
            
        # Update game state to reflect the capture
        if 'captured_pieces' not in room.game_state:
            room.game_state['captured_pieces'] = []
            
        room.game_state['captured_pieces'].append({
            'piece_id': piece_id,
            'position': position,
            'timestamp': datetime.now().isoformat()
        })
        
        # If the piece exists in pieces_state, mark it as captured
        if piece_id in room.game_state.get('pieces_state', {}):
            room.game_state['pieces_state'][piece_id]['state'] = 'captured'
        
        # Broadcast capture to all clients
        await room.broadcast_to_room({
            'type': 'piece_captured',
            'piece': {
                'id': piece_id,
                'position': position
            },
            'game_state': room.game_state
        })
        
        logger.info(f"Piece captured in room {room_id}: {piece_id} at {position}")
            
    async def cleanup_client(self, websocket: websockets.WebSocketServerProtocol):
        """Clean up when client disconnects."""
        room_id = self.client_rooms.get(websocket)
        if room_id and room_id in self.rooms:
            room = self.rooms[room_id]
            room.remove_player(websocket)
            room.remove_spectator(websocket)
            
            # Remove empty rooms
            if len(room.players) == 0 and len(room.spectators) == 0:
                del self.rooms[room_id]
                logger.info(f"Removed empty room {room_id}")
            else:
                # Notify remaining clients
                await room.broadcast_to_room({
                    'type': 'player_left',
                    'room_id': room_id,
                    'players_count': len(room.players),
                    'game_state': room.game_state
                })
        
        if websocket in self.client_rooms:
            del self.client_rooms[websocket]
    
    async def send_message(self, websocket: websockets.WebSocketServerProtocol, message: dict):
        """Send a message to a specific client."""
        try:
            await websocket.send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            pass
    
    async def start_server(self):
        """Start the WebSocket server."""
        logger.info(f"Starting Chess WebSocket Server on {self.host}:{self.port}")
        
        async with websockets.serve(self.register_client, self.host, self.port):
            logger.info("Chess WebSocket Server is running...")
            logger.info(f"Connect clients to: ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever


async def main():
    """Main entry point for the WebSocket server."""
    server = ChessWebSocketServer()
    
    try:
        await server.start_server()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        logger.info("Chess WebSocket Server stopped")


if __name__ == "__main__":
    asyncio.run(main())
