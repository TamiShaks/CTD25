def main():
    import csv
    import os
    from It1_interfaces.Game import Game
    from It1_interfaces.Board import Board
    from It1_interfaces.Piece import Piece
    from It1_interfaces.Moves import Moves
    from It1_interfaces.Graphics import Graphics
    from It1_interfaces.Physics import Physics
    from It1_interfaces.State import State
    from It1_interfaces.img import Img
    from It1_interfaces.EventBus import EventBus
    from It1_interfaces.ScoreManager import ScoreManager
    from It1_interfaces.MoveLogger import MoveLogger
    from It1_interfaces.SoundManager import SoundManager
    from It1_interfaces.AnimationManager import AnimationManager
    import pathlib

    # Initialize EventBus and managers
    event_bus = EventBus()
    sound_manager = SoundManager()
    score_manager = ScoreManager()
    move_logger = MoveLogger()
    animation_manager = AnimationManager()

    # Subscribe managers to events
    from It1_interfaces.EventTypes import MOVE_DONE, PIECE_CAPTURED, GAME_STARTED, GAME_ENDED
    event_bus.subscribe(MOVE_DONE, sound_manager)
    event_bus.subscribe(PIECE_CAPTURED, sound_manager)
    event_bus.subscribe(GAME_STARTED, sound_manager)
    event_bus.subscribe(GAME_ENDED, sound_manager)
    event_bus.subscribe(MOVE_DONE, score_manager)
    event_bus.subscribe(PIECE_CAPTURED, score_manager)
    event_bus.subscribe(MOVE_DONE, move_logger)
    event_bus.subscribe(GAME_STARTED, animation_manager)
    event_bus.subscribe(GAME_ENDED, animation_manager)

    # Initialize the board image
    board_img = Img()
    try:
        board_img.read(pathlib.Path("board.png"), size=(512, 512))
        print("✅ Board image loaded successfully!")
    except Exception as e:
        print(f"⚠️ Error loading board image: {e}")
    
    if board_img.img is None:
        print("❌ Failed to load board.png")
        exit(1)

    # Initialize the board
    board = Board(cell_H_pix=64, cell_W_pix=64, W_cells=8, H_cells=8, img=board_img)

    # Load initial positions from board.csv
    pieces = []
    board_csv_path = os.path.join(os.path.dirname(__file__), "pieces", "board.csv")
    if not os.path.exists(board_csv_path):
        exit(1)

    with open(board_csv_path, "r") as file:
        reader = csv.reader(file)
        for row_idx, row in enumerate(reader):
            for col_idx, cell in enumerate(row):
                if cell:
                    if len(cell) < 2:
                        continue
                    if len(cell) == 2:
                        piece_type, color_char = cell[0], cell[1]
                    else:
                        continue
                    color = "White" if color_char == "W" else "Black"
                    piece_id = f"{cell}{row_idx}{col_idx}"
                    moves_path = pathlib.Path(f"pieces/{cell}/moves.txt")
                    moves = Moves(moves_path, dims=(8, 8))
                    
                    # Create all state graphics and physics
                    idle_graphics = Graphics(pathlib.Path(f"pieces/{cell}/states/idle/sprites"), cell_size=(64, 64))
                    move_graphics = Graphics(pathlib.Path(f"pieces/{cell}/states/move/sprites"), cell_size=(64, 64))
                    jump_graphics = Graphics(pathlib.Path(f"pieces/{cell}/states/jump/sprites"), cell_size=(64, 64))
                    short_rest_graphics = Graphics(pathlib.Path(f"pieces/{cell}/states/short_rest/sprites"), cell_size=(64, 64))
                    long_rest_graphics = Graphics(pathlib.Path(f"pieces/{cell}/states/long_rest/sprites"), cell_size=(64, 64))
                    
                    # Create separate physics for each state to maintain position correctly
                    idle_physics = Physics(start_cell=(row_idx, col_idx), board=board)
                    move_physics = Physics(start_cell=(row_idx, col_idx), board=board)
                    jump_physics = Physics(start_cell=(row_idx, col_idx), board=board)
                    short_rest_physics = Physics(start_cell=(row_idx, col_idx), board=board)
                    long_rest_physics = Physics(start_cell=(row_idx, col_idx), board=board)
                    
                    # Create states
                    from It1_interfaces.State import create_long_rest_state, create_short_rest_state, create_move_state
                    idle_state = State(moves, idle_graphics, idle_physics, "idle")
                    
                    # Create rest states that return to idle
                    short_rest_state = create_short_rest_state(idle_state, moves, short_rest_graphics, short_rest_physics)
                    long_rest_state = create_long_rest_state(idle_state, moves, long_rest_graphics, long_rest_physics)
                    
                    # Create action states
                    move_state = create_move_state(idle_state, moves, move_graphics, move_physics)
                    jump_state = State(moves, jump_graphics, jump_physics, "jump")
                    jump_state.set_transition("complete", short_rest_state)
                    
                    # Set up transitions from idle state
                    idle_state.set_transition("Move", move_state)  # Move command -> move state -> long rest -> idle
                    idle_state.set_transition("Jump", jump_state)  # Jump command -> jump state -> short rest -> idle
                    
                    # Create piece with idle state
                    piece = Piece(piece_id=piece_id, init_state=idle_state, piece_type=piece_type)
                    piece.color = color  # Add color property
                    pieces.append(piece)

    king_count = sum(1 for piece in pieces if piece.piece_type == 'K')
    if king_count != 2:
        exit(1)

    # Create the game instance with managers
    game = Game(pieces=pieces, board=board, event_bus=event_bus, 
                score_manager=score_manager, move_logger=move_logger)

    game.run()


if __name__ == "__main__":
    main()
