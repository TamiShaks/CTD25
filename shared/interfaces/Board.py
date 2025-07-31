"""Chess board with image storage and cell dimensions."""
from dataclasses import dataclass, field
import copy
from img import Img

@dataclass
class Board:
    cell_H_pix: int
    cell_W_pix: int
    W_cells: int
    H_cells: int
    img: Img
    original_img: Img = field(init=False, repr=False)

    def __post_init__(self):
        self.original_img = Img()
        self.original_img.img = copy.deepcopy(self.img.img)

    def clone(self) -> "Board":
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
        self.img.img = copy.deepcopy(self.original_img.img)
