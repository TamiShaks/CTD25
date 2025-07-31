import pathlib
from Graphics import Graphics

class GraphicsFactory:
    @staticmethod
    def create(sprites_dir: pathlib.Path, cfg: dict = None, cell_size: tuple[int, int] = (64, 64), state_name: str = "") -> Graphics:
        """
        Create a Graphics instance from sprites directory with optional config and cell size.

        Args:
            sprites_dir: Path to the folder with sprites.
            cfg: Optional config dict, may contain 'loop' (bool) and 'fps' (float).
            cell_size: Width and height in pixels of each cell (default 64x64).
            state_name: Name of the state this graphics belongs to.

        Returns:
            Graphics instance.
        """
        if cfg is None:
            cfg = {}

        loop = cfg.get('loop', True)
        fps = cfg.get('fps', 6.0)

        return Graphics(
            sprites_folder=sprites_dir,
            cell_size=cell_size,
            loop=loop,
            fps=fps,
            state_name=state_name
        )
