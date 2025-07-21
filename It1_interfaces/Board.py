# from dataclasses import dataclass

# from img import Img

# @dataclass
# class Board:
#     cell_H_pix: int
#     cell_W_pix: int
#     W_cells: int
#     H_cells: int
#     img: Img

#     # convenience, not required by dataclass
#     def clone(self) -> "Board":
#         """Clone the board with a copy of the image."""
#         pass 

from dataclasses import dataclass
from img import Img

@dataclass
class Board:
    cell_H_pix: int
    cell_W_pix: int
    W_cells: int
    H_cells: int
    img: Img

    def clone(self) -> "Board":
        """Clone the board with a copy of the image."""
        new_img = Img()
        if self.img.img is not None:
            new_img.img = self.img.img.copy()

        return Board(
            cell_H_pix=self.cell_H_pix,
            cell_W_pix=self.cell_W_pix,
            W_cells=self.W_cells,
            H_cells=self.H_cells,
            img=new_img
        )

    def reset_board(self):
        """Reset the board image (create a fresh copy)."""
        if self.img.img is not None:
            self.img.img = self.img.img.copy()

    def cell_to_pixel(self, row: int, col: int) -> tuple[int, int]:
        """Convert cell coordinates to pixel coordinates (top-left corner)."""
        x = col * self.cell_W_pix
        y = row * self.cell_H_pix
        return x, y

    def pixel_to_cell(self, x: int, y: int) -> tuple[int, int]:
        """Convert pixel coordinates to cell coordinates."""
        col = x // self.cell_W_pix
        row = y // self.cell_H_pix
        return row, col

    def is_valid_cell(self, row: int, col: int) -> bool:
        """Check if cell is within board boundaries."""
        return 0 <= row < self.H_cells and 0 <= col < self.W_cells

        """Check if cell coordinates are within board bounds."""
        return 0 <= row < self.H_cells and 0 <= col < self.W_cells