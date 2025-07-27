from dataclasses import dataclass, field
import copy
from .img import Img

@dataclass
class Board:
    cell_H_pix: int  # Height of a single cell in pixels
    cell_W_pix: int  # Width of a single cell in pixels
    W_cells: int     # Number of cells horizontally
    H_cells: int     # Number of cells vertically
    img: Img         # Current image of the board

    # This field stores a deep copy of the original image for reset purposes.
    original_img: Img = field(init=False, repr=False)

    def __post_init__(self):
        """
        Called automatically after dataclass initialization.
        Saves a deep copy of the initial image so the board can be reset later.
        """
        self.original_img = Img()
        self.original_img.img = copy.deepcopy(self.img.img)

    def clone(self) -> "Board":
        """
        Create a deep copy of this Board, including a deep copy of the image.

        Returns:
            Board: A new Board instance with a copied image and same dimensions.
        """
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
        """
        Reset the board's image to its original state using the stored copy.
        """
        self.img.img = copy.deepcopy(self.original_img.img)
