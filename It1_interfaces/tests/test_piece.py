import sys
import os
import numpy as np

# הוספת הנתיב של It1_interfaces אל נתיב החיפוש
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Piece import Piece


# מחלקות מזויפות (Mocks) כמו שהצעתי לך קודם

class FakeCommand:
    def __init__(self, piece_id):
        self.piece_id = piece_id

    @staticmethod
    def create_idle_command(start_ms, piece_id):
        return FakeCommand(piece_id)

class FakeState:
    def __init__(self):
        self.reset_called = False
        self.update_called = False

        self.graphics = self.FakeGraphics()
        self.physics = self.FakePhysics()

    class FakeGraphics:
        def get_img(self):
            return self.FakeSprite()

        class FakeSprite:
            def draw_on(self, img, x, y):
                pass

    class FakePhysics:
        def get_pos(self):
            return (10, 20)

    def get_state_after_command(self, cmd, now_ms):
        if getattr(cmd, 'command_type', '') == 'change':
            return FakeState()
        return self

    def reset(self, cmd):
        self.reset_called = True

    def update(self, now_ms):
        self.update_called = True
        return self

class FakeBoard:
    def __init__(self):
        self.img = self.FakeImg()
        self.cell_H_pix = 40
        self.cell_W_pix = 30

    class FakeImg:
        def __init__(self):
            self.img = np.zeros((100, 100, 3), dtype=np.uint8)

def test_on_command_ignores_wrong_piece():
    piece = Piece("p1", FakeState())
    cmd = FakeCommand("other")
    old_state = piece.current_state
    piece.on_command(cmd, 1000)
    assert piece.current_state is old_state

def test_on_command_cooldown_blocks():
    piece = Piece("p1", FakeState())
    piece.last_action_time = 1000
    cmd = FakeCommand("p1")
    old_state = piece.current_state
    piece.on_command(cmd, 1500)  # פחות מ-2000ms
    assert piece.current_state is old_state

def test_on_command_state_changes():
    piece = Piece("p1", FakeState())
    piece.last_action_time = 0
    class CmdChange(FakeCommand):
        command_type = 'change'
    cmd = CmdChange("p1")
    piece.on_command(cmd, 3000)
    assert piece.last_action_time == 3000
    assert piece.current_state != None

def test_reset_calls_state_reset():
    piece = Piece("p1", FakeState())
    piece.reset(0)
    assert piece.start_time == 0
    assert piece.last_action_time == 0
    assert piece.current_state.reset_called

def test_update_calls_state_update():
    piece = Piece("p1", FakeState())
    piece.update(1000)
    assert piece.current_state.update_called

def test_draw_on_board_runs_without_error():
    piece = Piece("p1", FakeState())
    board = FakeBoard()
    try:
        piece.draw_on_board(board, 0)
    except Exception:
        assert False, "draw_on_board raised Exception"

def test_draw_on_board_with_cooldown_overlay():
    piece = Piece("p1", FakeState())
    board = FakeBoard()
    piece.last_action_time = 0
    try:
        piece.draw_on_board(board, 1000)  # חצי קולדאון
    except Exception:
        assert False, "draw_on_board with cooldown raised Exception"

if __name__ == "__main__":
    test_on_command_ignores_wrong_piece()
    test_on_command_cooldown_blocks()
    test_on_command_state_changes()
    test_reset_calls_state_reset()
    test_update_calls_state_update()
    test_draw_on_board_runs_without_error()
    test_draw_on_board_with_cooldown_overlay()
    print("All Piece tests passed!")
