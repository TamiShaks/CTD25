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
    board_img.read(pathlib.Path("board.png"), size=(512, 512))

    if board_img.img is None:
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
                    sprites_folder = pathlib.Path(f"pieces/{cell}/states/idle/sprites")
                    moves = Moves(moves_path, dims=(8, 8))
                    graphics = Graphics(sprites_folder, cell_size=(64, 64))
                    physics = Physics(start_cell=(row_idx, col_idx), board=board)
                    state = State(moves, graphics, physics)
                    pieces.append(Piece(piece_id=piece_id, init_state=state, piece_type=piece_type))

    king_count = sum(1 for piece in pieces if piece.piece_type == 'K')
    if king_count != 2:
        exit(1)

    # Create the game instance
    game = Game(pieces=pieces, board=board, event_bus=event_bus)

    game.run()


if __name__ == "__main__":
    main()
