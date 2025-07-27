import unittest
from Board import Board
from img import Img

class TestBoard(unittest.TestCase):
    def setUp(self):
        self.img = Img()
        self.img.img = [[0]*8 for _ in range(8)]  # Dummy image data
        self.board = Board(
            cell_H_pix=60,
            cell_W_pix=60,
            W_cells=8,
            H_cells=8,
            img=self.img
        )

    def test_clone_board(self):
        clone = self.board.clone()
        self.assertIsInstance(clone, Board)
        self.assertEqual(clone.cell_H_pix, self.board.cell_H_pix)
        self.assertEqual(clone.cell_W_pix, self.board.cell_W_pix)
        self.assertEqual(clone.W_cells, self.board.W_cells)
        self.assertEqual(clone.H_cells, self.board.H_cells)
        self.assertIsNot(clone.img, self.board.img)
        self.assertEqual(clone.img.img, self.board.img.img)

    def test_reset_board(self):
        # Currently does nothing, just check it runs
        self.board.reset_board()

if __name__ == '__main__':
    unittest.main()    pip install pygame