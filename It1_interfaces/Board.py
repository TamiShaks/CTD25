# from dataclasses import dataclass
# import copy
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
#         new_img = Img()
#         new_img.img = copy.deepcopy(self.img.img)
#         return Board(
#             self.cell_H_pix,
#             self.cell_W_pix, 
#             self.W_cells,
#             self.H_cells,
#             new_img
#         )
#         """Check if cell is within board boundaries."""
#         return 0 <= row < self.H_cells and 0 <= col < self.W_cells

#         """Check if cell coordinates are within board bounds."""
#         return 0 <= row < self.H_cells and 0 <= col < self.W_cells

from dataclasses import dataclass
import copy
from img import Img

@dataclass
class Board:
    cell_H_pix: int
    cell_W_pix: int
    W_cells: int
    H_cells: int
    img: Img

    # convenience, not required by dataclass
    def clone(self) -> "Board":
        """Clone the board with a copy of the image."""
        new_img = Img()
        new_img.img = copy.deepcopy(self.img.img)
        return Board(
            self.cell_H_pix,
            self.cell_W_pix, 
            self.W_cells,
            self.H_cells,
            new_img
        )
    
    def reset_board(self):
        """Reset the board to its original state (if needed)."""
        # If you need to reset the board image to its original state,
        # you might need to store the original image separately
        pass
    