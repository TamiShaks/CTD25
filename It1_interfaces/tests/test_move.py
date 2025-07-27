import tempfile
import pathlib
import sys
import os


# הוספת הנתיב של It1_interfaces אל נתיב החיפוש
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Moves import Moves


def test_get_moves_out_of_bounds_filtered():
    #simulate a moves file with some out-of-bounds moves
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
        f.write("-1,0\n")  # up
        f.write("0,-1\n")  # left
        f.write("1,0\n")   # down
        f.write("0,1\n")   # right
        move_file_path = pathlib.Path(f.name)

    moves = Moves(move_file_path, dims=(8, 8))  # לוח 8×8

    # assuming starting position at (0, 0)
    start_r, start_c = 0, 0
    result = moves.get_moves(start_r, start_c)

    # avialable moves should be only down and right
    expected = [(1, 0), (0, 1)]

    assert set(result) == set(expected)

    move_file_path.unlink()

def test_get_moves_basic():
    # Create a temporary file to simulate the move definition file
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
        f.write("1,0\n")
        f.write("0,1\n")
        f.write("1,1:diagonal\n")
        move_file_path = pathlib.Path(f.name)

    board_dims = (8, 8)
    moves = Moves(move_file_path, board_dims)

    start_r, start_c = 3, 3
    results = moves.get_moves(start_r, start_c)
    expected = [(4, 3), (3, 4), (4, 4)]

    assert set(results) == set(expected)

    # Clean up the file
    move_file_path.unlink()

if __name__ == "__main__":
    test_get_moves_basic()
    print("✅ test_get_moves_basic passed.")
