"""
Debug script to test state transitions
"""

def main():
    import csv
    import os
    import pathlib
    from It1_interfaces.Game import Game
    from It1_interfaces.Board import Board
    from It1_interfaces.Piece import Piece
    from It1_interfaces.Moves import Moves
    from It1_interfaces.Graphics import Graphics
    from It1_interfaces.Physics import Physics
    from It1_interfaces.State import State, create_long_rest_state, create_short_rest_state, create_move_state
    from It1_interfaces.img import Img
    from It1_interfaces.Command import Command

    print("🔍 Testing state system...")
    
    # Create a simple board
    board_img = Img()
    board_img.read(pathlib.Path("board.png"), size=(512, 512))
    board = Board(cell_H_pix=64, cell_W_pix=64, W_cells=8, H_cells=8, img=board_img)
    
    # Create a test piece (White Pawn)
    moves_path = pathlib.Path("pieces/PW/moves.txt")
    moves = Moves(moves_path, dims=(8, 8))
    
    # Create graphics for all states
    idle_graphics = Graphics(pathlib.Path("pieces/PW/states/idle/sprites"), cell_size=(64, 64))
    move_graphics = Graphics(pathlib.Path("pieces/PW/states/move/sprites"), cell_size=(64, 64))
    long_rest_graphics = Graphics(pathlib.Path("pieces/PW/states/long_rest/sprites"), cell_size=(64, 64))
    
    # Create physics for all states
    idle_physics = Physics(start_cell=(6, 0), board=board)
    move_physics = Physics(start_cell=(6, 0), board=board)
    long_rest_physics = Physics(start_cell=(6, 0), board=board)
    
    # Create states with proper transitions
    idle_state = State(moves, idle_graphics, idle_physics, "idle")
    move_state = create_move_state(idle_state, moves, move_graphics, move_physics)
    
    # Set up transitions
    idle_state.set_transition("Move", move_state)
    
    # Create piece
    piece = Piece(piece_id="PW60", init_state=idle_state, piece_type="P")
    piece.color = "White"
    
    print(f"✅ Created piece {piece.piece_id} in state: {piece.current_state.state}")
    print(f"📋 Available transitions from idle: {list(piece.current_state.transitions.keys())}")
    
    # Test move command
    now = 1000  # 1 second
    move_cmd = Command.create_move_command(now, piece.piece_id, (6, 0), (5, 0))
    
    print(f"\n🎯 Sending move command...")
    print(f"Command: {move_cmd}")
    print(f"Piece state before: {piece.current_state.state}")
    
    piece.on_command(move_cmd, now)
    
    print(f"Piece state after: {piece.current_state.state}")
    
    # Test update loop
    print(f"\n🔄 Testing updates...")
    for i in range(10):
        now += 100  # Add 100ms each iteration
        old_state = piece.current_state.state
        piece.update(now)
        if old_state != piece.current_state.state:
            print(f"Time {now}ms: State changed from {old_state} to {piece.current_state.state}")

if __name__ == "__main__":
    main()
