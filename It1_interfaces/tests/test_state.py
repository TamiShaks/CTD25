import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from State import State, create_long_rest_state, create_short_rest_state
from Command import Command

# Mock classes
class MockGraphics:
    def __init__(self):
        self.reset_called = False
        self.updated_at = None

    def reset(self, cmd):
        self.reset_called = True
        self.last_command = cmd

    def update(self, now_ms):
        self.updated_at = now_ms

    def copy(self):
        return MockGraphics()

class MockPhysics:
    def __init__(self):
        self.reset_called = False
        self.updated_at = None

    def reset(self, cmd):
        self.reset_called = True
        self.last_command = cmd

    def update(self, now_ms):
        self.updated_at = now_ms

class MockMoves:
    pass

# ---- TESTS ----

def test_reset_sets_initial_state():
    graphics = MockGraphics()
    physics = MockPhysics()
    moves = MockMoves()
    state = State(moves, graphics, physics)
    cmd = Command(1234, "p1", "idle", [])
    state.reset(cmd)

    assert state.current_command == cmd
    assert graphics.reset_called
    assert physics.reset_called
    assert state.state_start_time == 1234

def test_can_transition_non_rest_state_returns_true():
    state = State(MockMoves(), MockGraphics(), MockPhysics())
    now = 2000
    assert state.can_transition(now) is True

def test_rest_state_blocks_transition_until_timeout():
    state = State(MockMoves(), MockGraphics(), MockPhysics())
    state.is_rest_state = True
    state.rest_duration_ms = 1000
    state.state_start_time = 5000

    assert state.can_transition(5500) is False
    assert state.can_transition(6001) is True

def test_get_state_after_command_with_transition():
    idle = State(MockMoves(), MockGraphics(), MockPhysics())
    move = State(MockMoves(), MockGraphics(), MockPhysics())
    idle.set_transition("Move", move)

    cmd = Command(1234, "p1", "Move", [(0, 0), (1, 1)])

    # מחקים את מה שהקוד אמור לעשות במקום copy()
    original_next_state = idle.transitions["Move"]
    next_state = State(original_next_state.moves, original_next_state.graphics.copy(), original_next_state.physics)
    next_state.reset(cmd)

    result_state = idle.get_state_after_command(cmd, now_ms=2000)

    assert result_state.current_command == next_state.current_command
    assert isinstance(result_state, State)
    assert result_state is not idle
    assert result_state.current_command == cmd

def test_get_state_after_command_no_transition():
    idle = State(MockMoves(), MockGraphics(), MockPhysics())
    cmd = Command(1234, "p1", "Jump", [(1, 1), (2, 2)])
    result = idle.get_state_after_command(cmd, 2000)
    assert result is idle

def test_update_calls_graphics_and_physics_update():
    g = MockGraphics()
    p = MockPhysics()
    state = State(MockMoves(), g, p)
    now = 3000
    state.update(now)

    assert g.updated_at == now
    assert p.updated_at == now

def test_rest_state_transitions_on_timeout():
    idle = State(MockMoves(), MockGraphics(), MockPhysics())
    rest = create_short_rest_state(idle)
    rest.state_start_time = 0  # סימולציה של זמן התחלה
    now = 1500  # > 1000ms

    new_state = rest.update(now)
    assert new_state is not rest
    assert isinstance(new_state, State)
    assert new_state.current_command.type == "timeout"

def test_create_long_rest_state_sets_properties():
    idle = State(MockMoves(), MockGraphics(), MockPhysics())
    long_rest = create_long_rest_state(idle)

    assert long_rest.is_rest_state
    assert long_rest.rest_duration_ms == 2000
    assert "timeout" in long_rest.transitions
    assert long_rest.transitions["timeout"] is idle

# ---- RUN ----

if __name__ == "__main__":
    test_reset_sets_initial_state()
    test_can_transition_non_rest_state_returns_true()
    test_rest_state_blocks_transition_until_timeout()
    test_get_state_after_command_with_transition()
    test_get_state_after_command_no_transition()
    test_update_calls_graphics_and_physics_update()
    test_rest_state_transitions_on_timeout()
    test_create_long_rest_state_sets_properties()
    print("✅ All tests passed successfully!")
