import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Board import Board
from img import Img
def test_clone_creates_independent_copy():
    original_img = Img()
    original_img.img = [[1, 2], [3, 4]]

    board = Board(100, 100, 8, 8, original_img)
    cloned_board = board.clone()

    # נבדוק שהעותק לא אותו אובייקט
    assert cloned_board is not board
    assert cloned_board.img is not board.img
    assert cloned_board.img.img != None

    # שינוי בעותק לא משפיע על המקור
    cloned_board.img.img[0][0] = 999
    assert board.img.img[0][0] == 1


def test_reset_board_restores_original_state():
    original_img = Img()
    original_img.img = [[1, 2], [3, 4]]

    board = Board(100, 100, 8, 8, original_img)
    board.img.img[0][0] = 999  # שינוי

    board.reset_board()

    assert board.img.img == [[1, 2], [3, 4]], "Reset did not restore the original image"
if __name__ == "__main__":
    test_clone_creates_independent_copy()
    test_reset_board_restores_original_state()
    print("All tests passed!")