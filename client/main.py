def main():
    # Show game start screen for 1 second
    print("🎮 Loading game start screen...")
    try:
        import pygame
        import time
        
        pygame.init()
        pygame.display.init()
        
        begin_image = pygame.image.load("client/pictures/begin.jpg")
        screen = pygame.display.set_mode((1024, 768))
        pygame.display.set_caption("🎮 Chess Game Starting...")
        
        # Scale and center image
        img_rect = begin_image.get_rect()
        screen_rect = screen.get_rect()
        scale = min(screen_rect.width / img_rect.width, screen_rect.height / img_rect.height, 1.0)
        new_size = (int(img_rect.width * scale), int(img_rect.height * scale))
        scaled_image = pygame.transform.scale(begin_image, new_size)
        img_rect = scaled_image.get_rect(center=screen_rect.center)
        
        screen.fill((0, 0, 0))
        screen.blit(scaled_image, img_rect)
        pygame.display.flip()
        
        print("✅ Start screen displayed! Waiting 1 second...")
        time.sleep(1)
        print("🎯 Loading game...")
        pygame.quit()
        
    except Exception as e:
        print(f"⚠️ Warning: Could not show start screen: {e}")
        try:
            pygame.quit()
        except:
            pass
    
    import csv
    import os
    import sys
    from pathlib import Path
    
    # Add paths to client, server, and shared components
    base_path = Path(__file__).parent.parent
    sys.path.append(str(base_path / "server" / "interfaces"))
    sys.path.append(str(base_path / "client" / "interfaces"))
    sys.path.append(str(base_path / "shared" / "interfaces"))
    
    from Game import Game
    from Board import Board
    from Piece import Piece
    from Moves import Moves
    from Graphics import Graphics
    from Physics import Physics
    from State import State
    from img import Img
    from EventBus import EventBus
    from ScoreManager import ScoreManager
    from SoundManager import SoundManager
    from AnimationManager import AnimationManager
    import pathlib

    from MoveLogger import MoveLogger

    def create_piece_states(cell, row_idx, col_idx, board):
        """Create all states for a piece."""
        moves_path = pathlib.Path(f"shared/pieces/{cell}/moves.txt")
        moves = Moves(moves_path, (8, 8))
        
        # Create graphics for all states
        states_path = pathlib.Path(f"shared/pieces/{cell}/states")
        idle_graphics = Graphics(states_path / "idle/sprites", cell_size=(64, 64))
        move_graphics = Graphics(states_path / "move/sprites", cell_size=(64, 64))
        jump_graphics = Graphics(states_path / "jump/sprites", cell_size=(64, 64))
        short_rest_graphics = Graphics(states_path / "short_rest/sprites", cell_size=(64, 64))
        long_rest_graphics = Graphics(states_path / "long_rest/sprites", cell_size=(64, 64))
        
        # Create physics for all states
        start_cell = (row_idx, col_idx)
        idle_physics = Physics(start_cell, board)
        move_physics = Physics(start_cell, board)
        jump_physics = Physics(start_cell, board)
        short_rest_physics = Physics(start_cell, board)
        long_rest_physics = Physics(start_cell, board)
        
        # Create states
        from State import create_long_rest_state, create_short_rest_state, create_move_state
        idle_state = State(moves, idle_graphics, idle_physics, "idle")
        
        # Create rest states that return to idle
        short_rest_state = create_short_rest_state(idle_state, moves, short_rest_graphics, short_rest_physics)
        long_rest_state = create_long_rest_state(idle_state, moves, long_rest_graphics, long_rest_physics)
        
        # Create action states
        move_state = create_move_state(idle_state, moves, move_graphics, move_physics)
        jump_state = State(moves, jump_graphics, jump_physics, "jump")
        jump_state.set_transition("complete", short_rest_state)
        
        # Set up transitions from idle state
        idle_state.set_transition("Move", move_state)
        idle_state.set_transition("Jump", jump_state)
        
        return idle_state

    # Initialize EventBus and managers
    event_bus = EventBus()
    sound_manager = SoundManager()
    score_manager = ScoreManager()
    move_logger = MoveLogger()
    animation_manager = AnimationManager()

    # Subscribe managers to events
    from EventTypes import MOVE_DONE, PIECE_CAPTURED, GAME_STARTED, GAME_ENDED, INVALID_MOVE
    event_bus.subscribe(MOVE_DONE, sound_manager)
    event_bus.subscribe(PIECE_CAPTURED, sound_manager)
    event_bus.subscribe(GAME_STARTED, sound_manager)
    event_bus.subscribe(GAME_ENDED, sound_manager)
    event_bus.subscribe(INVALID_MOVE, sound_manager)  # NEW: Sound for invalid moves
    event_bus.subscribe(MOVE_DONE, score_manager)
    event_bus.subscribe(PIECE_CAPTURED, score_manager)
    event_bus.subscribe(MOVE_DONE, move_logger)
    event_bus.subscribe(GAME_STARTED, animation_manager)
    event_bus.subscribe(GAME_ENDED, animation_manager)

    # Initialize the board image
    board_img = Img()
    try:
        board_img.read(pathlib.Path("shared/board.png"), size=(512, 512))
        print("Board image loaded successfully!")
    except Exception as e:
        print(f"Error loading board image: {e}")
    
    if board_img.img is None:
        print("Failed to load board.png")
        exit(1)

    # Initialize the board
    board = Board(cell_H_pix=64, cell_W_pix=64, W_cells=8, H_cells=8, img=board_img)

    # Load initial positions from board.csv
    pieces = []
    board_csv_path = "shared/pieces/board.csv"
    if not os.path.exists(board_csv_path):
        exit(1)

    with open(board_csv_path, "r") as file:
        reader = csv.reader(file)
        for row_idx, row in enumerate(reader):
            for col_idx, cell in enumerate(row):
                if cell and len(cell) == 2:
                    piece_type, color_char = cell[0], cell[1]
                    color = "White" if color_char == "W" else "Black"
                    piece_id = f"{cell}{row_idx}{col_idx}"
                    
                    # Create piece with all its states
                    idle_state = create_piece_states(cell, row_idx, col_idx, board)
                    piece = Piece(piece_id=piece_id, initial_state=idle_state, piece_type=piece_type)
                    piece.color = color
                    pieces.append(piece)

    king_count = sum(1 for piece in pieces if piece.piece_type == 'K')
    if king_count != 2:
        exit(1)

    # Create the game instance with managers
    game = Game(pieces=pieces, board=board, event_bus=event_bus, 
                score_manager=score_manager, move_logger=move_logger)

    # Ask user for game mode
    print("\n🎮 Chess Game - Choose Mode:")
    print("1. 👤 Local Game (Single Computer)")
    print("2. 🌐 Create Online Room")
    print("3. 🔗 Join Online Room")
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == "2":
        # Network game - create room
        from network_game_manager import NetworkGameManager
        network_manager = NetworkGameManager(game, event_bus)
        
        print("🌐 Starting online game...")
        if network_manager.start_network_game("create"):
            print("✅ Network game started!")
            
            # Integrate network manager with game loop
            game.network_manager = network_manager
        else:
            print("❌ Failed to start network game. Playing locally.")
            
    elif choice == "3":
        # Network game - join room
        room_id = input("Enter Room ID: ").strip()
        if room_id:
            from network_game_manager import NetworkGameManager
            network_manager = NetworkGameManager(game, event_bus)
            
            print(f"🔗 Joining room {room_id}...")
            if network_manager.start_network_game("join", room_id):
                print("✅ Joined network game!")
                
                # Integrate network manager with game loop
                game.network_manager = network_manager
            else:
                print("❌ Failed to join room. Playing locally.")
        else:
            print("❌ Invalid room ID. Playing locally.")
    
    # Default to local game
    if choice not in ["2", "3"]:
        print("🎮 Starting local game...")

    game.run()


if __name__ == "__main__":
    main()
