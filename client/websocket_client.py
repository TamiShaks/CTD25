"""
WebSocket Chess Client
Handles connection to the chess server and network communication.
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime
from typing import Optional, Callable, Dict, Any
import threading
import queue

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ChessWebSocketClient:
    """WebSocket client for chess game communication."""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.uri = f"ws://{host}:{port}"
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False
        self.room_id: Optional[str] = None
        self.player_color: Optional[str] = None
        
        # Message queues for communication with main thread
        self.incoming_messages = queue.Queue()
        self.outgoing_messages = queue.Queue()
        
        # Event callbacks
        self.on_connected: Optional[Callable] = None
        self.on_disconnected: Optional[Callable] = None
        self.on_room_created: Optional[Callable[[str, str]]] = None  # room_id, color
        self.on_room_joined: Optional[Callable[[str, str]]] = None   # room_id, color
        self.on_move_received: Optional[Callable[[Dict]]] = None
        self.on_player_joined: Optional[Callable[[Dict]]] = None
        self.on_player_left: Optional[Callable[[Dict]]] = None
        self.on_chat_message: Optional[Callable[[Dict]]] = None
        self.on_error: Optional[Callable[[str]]] = None
        self.on_game_state_received: Optional[Callable[[Dict]]] = None
        
        # Background thread for websocket communication
        self.websocket_thread: Optional[threading.Thread] = None
        self.should_stop = False
        
        logger.info(f"Chess WebSocket Client initialized for {self.uri}")
    
    def start_connection(self):
        """Start the WebSocket connection in a background thread."""
        if self.websocket_thread and self.websocket_thread.is_alive():
            logger.warning("WebSocket connection already running")
            return
        
        self.should_stop = False
        self.websocket_thread = threading.Thread(target=self._run_websocket_loop, daemon=True)
        self.websocket_thread.start()
        logger.info("WebSocket connection thread started")
    
    def stop_connection(self):
        """Stop the WebSocket connection."""
        self.should_stop = True
        if self.websocket_thread:
            self.websocket_thread.join(timeout=2.0)
        logger.info("WebSocket connection stopped")
    
    def _run_websocket_loop(self):
        """Run the WebSocket event loop in the background thread."""
        try:
            asyncio.run(self._websocket_handler())
        except Exception as e:
            logger.error(f"WebSocket loop error: {e}")
            if self.on_error:
                self.on_error(f"Connection error: {e}")
    
    async def _websocket_handler(self):
        """Handle WebSocket connection and message processing."""
        try:
            logger.info(f"Connecting to {self.uri}")
            async with websockets.connect(self.uri) as websocket:
                self.websocket = websocket
                self.connected = True
                logger.info("Connected to chess server")
                
                if self.on_connected:
                    self.on_connected()
                
                # Create tasks for sending and receiving
                receive_task = asyncio.create_task(self._receive_messages())
                send_task = asyncio.create_task(self._send_messages())
                
                # Wait for either task to complete (or connection to close)
                done, pending = await asyncio.wait(
                    [receive_task, send_task],
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Cancel pending tasks
                for task in pending:
                    task.cancel()
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            if self.on_error:
                self.on_error(f"Connection failed: {e}")
        finally:
            self.connected = False
            self.websocket = None
            if self.on_disconnected:
                self.on_disconnected()
    
    async def _receive_messages(self):
        """Receive messages from the WebSocket server."""
        while not self.should_stop and self.websocket:
            try:
                message = await self.websocket.recv()
                data = json.loads(message)
                
                # Put message in queue for main thread to process
                self.incoming_messages.put(data)
                logger.debug(f"Received message: {data.get('type', 'unknown')}")
                
            except websockets.exceptions.ConnectionClosed:
                break
            except json.JSONDecodeError:
                logger.error("Received invalid JSON message")
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
                break
    
    async def _send_messages(self):
        """Send messages from the queue to the WebSocket server."""
        while not self.should_stop and self.websocket:
            try:
                # Non-blocking check for outgoing messages
                await asyncio.sleep(0.01)  # Small delay to prevent busy waiting
                
                while not self.outgoing_messages.empty():
                    try:
                        message = self.outgoing_messages.get_nowait()
                        # Include current timestamp in the message
                        if isinstance(message, dict):
                            message['timestamp'] = datetime.now().timestamp()
                        
                        await self.websocket.send(json.dumps(message))
                        logger.debug(f"Sent message: {message.get('type', 'unknown')}")
                    except queue.Empty:
                        break
                        
            except websockets.exceptions.ConnectionClosed:
                break
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                break
    
    def process_incoming_messages(self):
        """Process incoming messages in the main thread."""
        while not self.incoming_messages.empty():
            try:
                data = self.incoming_messages.get_nowait()
                self._handle_message(data)
            except queue.Empty:
                break
    
    def _handle_message(self, data: Dict[str, Any]):
        """Handle incoming message based on type."""
        message_type = data.get('type')
        
        if message_type == 'connection_established':
            logger.info("Connection established with server")
            
        elif message_type == 'room_created':
            self.room_id = data.get('room_id')
            self.player_color = data.get('player_color')
            logger.info(f"Room created: {self.room_id}, playing as {self.player_color}")
            if self.on_room_created:
                self.on_room_created(self.room_id, self.player_color)
                
        elif message_type == 'room_joined':
            self.room_id = data.get('room_id')
            self.player_color = data.get('player_color')
            logger.info(f"Joined room: {self.room_id}, role: {self.player_color}")
            if self.on_room_joined:
                self.on_room_joined(self.room_id, self.player_color)
                
        elif message_type == 'move_made':
            piece_info = data.get('piece', {})
            if piece_info:
                logger.info(f"Network move received:")
                logger.info(f"  Piece: {piece_info.get('piece')}")
                logger.info(f"  From: {piece_info.get('from')} → {piece_info.get('to')}")
                logger.info(f"  State: {piece_info.get('state')}")
                logger.info(f"  Speed: {piece_info.get('speed')}")
                
                if self.on_move_received:
                    self.on_move_received(piece_info)
                
        elif message_type == 'player_joined':
            logger.info(f"Player joined room {data.get('room_id')}")
            if self.on_player_joined:
                self.on_player_joined(data)
                
        elif message_type == 'player_left':
            logger.info(f"Player left room {data.get('room_id')}")
            if self.on_player_left:
                self.on_player_left(data)
                
        elif message_type == 'chat_message':
            logger.info(f"Chat message from {data.get('player')}: {data.get('message')}")
            if self.on_chat_message:
                self.on_chat_message(data)
                
        elif message_type == 'error':
            error_msg = data.get('message', 'Unknown error')
            logger.error(f"Server error: {error_msg}")
            if self.on_error:
                self.on_error(error_msg)
                
        elif message_type == 'game_state':
            state_data = data.get('state', {})
            logger.info(f"Game state received with {len(state_data.get('pieces', []))} pieces")
            if self.on_game_state_received:
                self.on_game_state_received(state_data)
                
        elif message_type == 'pong':
            logger.debug("Received pong from server")
            
        else:
            logger.warning(f"Unknown message type: {message_type}")
    
    def send_message(self, message: Dict[str, Any]):
        """Send a message to the server."""
        if not self.connected:
            logger.warning("Cannot send message: not connected")
            return False
        
        self.outgoing_messages.put(message)
        return True
    
    def create_room(self) -> bool:
        """Create a new game room."""
        return self.send_message({'type': 'create_room'})
    
    def join_room(self, room_id: str) -> bool:
        """Join an existing game room."""
        return self.send_message({
            'type': 'join_room',
            'room_id': room_id
        })
    
    def list_rooms(self) -> bool:
        """Request list of available rooms."""
        return self.send_message({'type': 'list_rooms'})
    
    def make_move(self, from_pos: str, to_pos: str, piece: str, state_info: dict = None) -> bool:
        """Send a chess move to the server with complete state info."""
        if not state_info:
            state_info = {
                'name': 'moving',
                'speed': 1.0,
                'is_rest': False,
                'rest_duration': 0,
                'activation_time': 0,
                'transitions': {}
            }
            
        return self.send_message({
            'type': 'make_move',
            'from': from_pos,
            'to': to_pos,
            'piece': piece,
            'state_info': state_info
        })
        
    def notify_piece_captured(self, piece_id: str, position: str) -> bool:
        """Notify server about a captured piece."""
        return self.send_message({
            'type': 'piece_captured',
            'piece': {
                'id': piece_id,
                'position': position
            }
        })
    
    def send_chat_message(self, message: str) -> bool:
        """Send a chat message."""
        return self.send_message({
            'type': 'chat_message',
            'message': message
        })
    
    def ping(self) -> bool:
        """Send ping to server."""
        return self.send_message({'type': 'ping'})
    
    def is_connected(self) -> bool:
        """Check if connected to server."""
        return self.connected
    
    def get_room_info(self) -> Dict[str, Optional[str]]:
        """Get current room information."""
        return {
            'room_id': self.room_id,
            'player_color': self.player_color
        }
