from Command import Command
from Moves import Moves
from Graphics import Graphics  
from Physics import Physics
from typing import Dict, Optional
import pathlib


class GamePieceSpritesPathManager:
    """Self-documenting utility for managing chess piece sprite folder paths."""
    
    @staticmethod
    def determine_piece_type_from_sprites_directory_path(sprites_folder_path) -> Optional[str]:
        """Extract piece type from sprites folder path like 'pieces/PW/states/idle/sprites'"""
        if isinstance(sprites_folder_path, str):
            path = pathlib.Path(sprites_folder_path)
        else:
            path = sprites_folder_path
        
        # Extract piece type from path structure: pieces/{PIECE_TYPE}/states/{STATE}/sprites
        parts = path.parts
        if len(parts) >= 4 and parts[-3] == 'states' and parts[-1] == 'sprites':
            return parts[-4]
        return None

    @staticmethod
    def build_sprites_directory_path_for_target_state(current_sprites_folder, target_state_name):
        """Construct correct sprites folder path for target state"""
        piece_type = GamePieceSpritesPathManager.determine_piece_type_from_sprites_directory_path(current_sprites_folder)
        if piece_type:
            # Construct: pieces/{piece_type}/states/{target_state_name}/sprites
            return pathlib.Path("shared/pieces") / piece_type / "states" / target_state_name / "sprites"
        return current_sprites_folder  # Fallback to current if extraction fails


class GamePieceStateManager:
    """Self-documenting chess piece state manager with transitions and behaviors."""
    
    def __init__(self, movement_rules: Moves, visual_renderer: Graphics, 
                 movement_physics: Physics, state_identifier: str = "idle"):
        self.movement_rules = movement_rules
        self.visual_renderer = visual_renderer
        self.movement_physics = movement_physics
        self.state_transition_mapping: Dict[str, "GamePieceStateManager"] = {}
        self.state_activation_timestamp = 0
        self.active_command = None
        
        # State-specific properties
        self.requires_rest_period = False
        self.rest_period_duration_ms = 0
        self.current_state_name = state_identifier

    def create_independent_copy_of_state(self) -> "GamePieceStateManager":
        """Create a deep copy of this state."""
        new_visual_renderer = self.visual_renderer.copy()
        new_visual_renderer.state_name = self.current_state_name
        new_movement_physics = self.movement_physics.create_independent_copy()
    
        new_state = GamePieceStateManager(self.movement_rules, new_visual_renderer, 
                                        new_movement_physics, self.current_state_name)
        new_state.state_transition_mapping = {}  # Transitions will be set up separately
        new_state.requires_rest_period = self.requires_rest_period
        new_state.rest_period_duration_ms = self.rest_period_duration_ms
    
        return new_state

    def configure_state_transition_rule(self, triggering_event: str, destination_state: "GamePieceStateManager"):
        """Set a transition from this state to another state on an event."""
        self.state_transition_mapping[triggering_event] = destination_state

    def build_new_state_from_transition_template(self, template_state: "GamePieceStateManager", 
                                                cmd: Command) -> "GamePieceStateManager":
        """Create a new state instance from a template state and command."""
        next_state = self.create_base_state_copy_from_template(template_state)
        next_state.visual_renderer = self.create_visual_renderer_for_target_state(template_state)
        self.transfer_physics_state_to_new_state(next_state)
        next_state.activate_state_with_command(cmd)
        return next_state

    def create_base_state_copy_from_template(self, template_state: "GamePieceStateManager") -> "GamePieceStateManager":
        """Create base transition state with properties copied from template."""
        next_state = self.create_independent_copy_of_state()
        next_state.current_state_name = template_state.current_state_name
        next_state.requires_rest_period = template_state.requires_rest_period
        next_state.rest_period_duration_ms = template_state.rest_period_duration_ms
        next_state.state_transition_mapping = template_state.state_transition_mapping.copy()
        return next_state

    def create_visual_renderer_for_target_state(self, template_state: "GamePieceStateManager") -> Graphics:
        """Create new Graphics object with correct state name and sprites folder."""
        from GraphicsFactory import GraphicsFactory
        
        correct_sprites_folder = GamePieceSpritesPathManager.build_sprites_directory_path_for_target_state(
            template_state.visual_renderer.sprites_folder, 
            template_state.current_state_name
        )
        
        return GraphicsFactory.create(
            correct_sprites_folder,
            {},  # Empty config - use defaults
            template_state.visual_renderer.cell_size,
            template_state.current_state_name
        )

    def transfer_physics_state_to_new_state(self, target_state: "GamePieceStateManager"):
        """Copy current physics state to the next state."""
        if hasattr(self.movement_physics, 'current_cell'):
            target_state.movement_physics.current_cell = self.movement_physics.current_cell
            target_state.movement_physics.target_cell = self.movement_physics.target_cell

    def activate_state_with_command(self, cmd: Command):
        """Reset the state with a new command."""
        self.active_command = cmd
        self.state_activation_timestamp = cmd.timestamp
        self.visual_renderer.reset(cmd)
        self.movement_physics.execute_command_physics(cmd)

    def check_if_state_transition_is_allowed(self, current_time_ms: int) -> bool:
        """Check if the state can transition."""
        if self.requires_rest_period:
            elapsed = current_time_ms - self.state_activation_timestamp
            return elapsed >= self.rest_period_duration_ms
        return True  # Non-rest states can always transition

    # Backward compatibility aliases
    def copy(self) -> "GamePieceStateManager":
        return self.create_independent_copy_of_state()
    
    def set_transition(self, event: str, target: "GamePieceStateManager"):
        return self.configure_state_transition_rule(event, target)
    
    def _create_transition_state(self, template_state: "GamePieceStateManager", cmd: Command) -> "GamePieceStateManager":
        return self.build_new_state_from_transition_template(template_state, cmd)
    
    def _create_base_transition_state(self, template_state: "GamePieceStateManager") -> "GamePieceStateManager":
        return self.create_base_state_copy_from_template(template_state)
    
    def _create_graphics_for_state(self, template_state: "GamePieceStateManager") -> Graphics:
        return self.create_visual_renderer_for_target_state(template_state)
    
    def _copy_physics_state(self, next_state: "GamePieceStateManager"):
        return self.transfer_physics_state_to_new_state(next_state)
    
    def reset(self, cmd: Command):
        return self.activate_state_with_command(cmd)
    
    def can_transition(self, now_ms: int) -> bool:
        return self.check_if_state_transition_is_allowed(now_ms)
    
    # Property aliases for backward compatibility
    @property
    def moves(self):
        return self.movement_rules
    
    @moves.setter
    def moves(self, value):
        self.movement_rules = value
    
    @property
    def graphics(self):
        return self.visual_renderer
    
    @property
    def physics(self):
        return self.movement_physics
    
    @property
    def transitions(self):
        return self.state_transition_mapping
    
    @property
    def state_start_time(self):
        return self.state_activation_timestamp
    
    @property
    def current_command(self):
        return self.active_command
    
    @property
    def is_rest_state(self):
        return self.requires_rest_period
    
    @is_rest_state.setter
    def is_rest_state(self, value):
        self.requires_rest_period = value
    
    @property
    def rest_duration_ms(self):
        return self.rest_period_duration_ms
    
    @rest_duration_ms.setter
    def rest_duration_ms(self, value):
        self.rest_period_duration_ms = value
    
    @property
    def state(self):
        return self.current_state_name
    
    @state.setter
    def state(self, value):
        self.current_state_name = value

    def calculate_next_state_after_command_execution(self, cmd: Command, current_time_ms: int) -> "GamePieceStateManager":
        """Get the next state after processing a command."""
        if not self.check_if_state_transition_is_allowed(current_time_ms):
            return self  # Stay in current state if can't transition
            
        if cmd.type in self.state_transition_mapping:
            template_state = self.state_transition_mapping[cmd.type]
            return self.build_new_state_from_transition_template(template_state, cmd)
        return self

    def update_state_and_check_for_transitions(self, current_time_ms: int) -> "GamePieceStateManager":
        """Update the state based on current time."""
        self.visual_renderer.update(current_time_ms)
        movement_complete = self.movement_physics.update_movement_state(current_time_ms)
        
        # Check for completion transitions
        if movement_complete and "complete" in self.state_transition_mapping:
            return self.execute_completion_state_transition(current_time_ms)

        # Check for timeout transitions
        if (self.requires_rest_period and self.check_if_state_transition_is_allowed(current_time_ms) 
            and "timeout" in self.state_transition_mapping):
            return self.execute_timeout_state_transition(current_time_ms)
        
        # Handle specific state auto-completion
        return self.handle_automatic_state_transitions(current_time_ms)

    def execute_completion_state_transition(self, current_time_ms: int) -> "GamePieceStateManager":
        """Handle completion transition."""
        template_state = self.state_transition_mapping["complete"]
        completion_cmd = Command(current_time_ms, "", "complete", [])
        return self.build_new_state_from_transition_template(template_state, completion_cmd)

    def execute_timeout_state_transition(self, current_time_ms: int) -> "GamePieceStateManager":
        """Handle timeout transition."""
        template_state = self.state_transition_mapping["timeout"]
        timeout_cmd = Command(current_time_ms, "", "timeout", [])
        return self.build_new_state_from_transition_template(template_state, timeout_cmd)

    def handle_automatic_state_transitions(self, current_time_ms: int) -> "GamePieceStateManager":
        """Handle state-specific update logic."""
        if self.current_state_name == "move" and not self.movement_physics.is_moving:
            return self.calculate_next_state_after_command_execution(
                Command(current_time_ms, "", "complete", []), current_time_ms)
        return self
    
    def retrieve_active_command(self) -> Command:
        """Get the current command for this state."""
        return self.active_command

    # Additional backward compatibility methods
    def get_state_after_command(self, cmd: Command, now_ms: int) -> "GamePieceStateManager":
        return self.calculate_next_state_after_command_execution(cmd, now_ms)
    
    def update(self, now_ms: int) -> "GamePieceStateManager":
        return self.update_state_and_check_for_transitions(now_ms)
    
    def _handle_completion_transition(self, now_ms: int) -> "GamePieceStateManager":
        return self.execute_completion_state_transition(now_ms)
    
    def _handle_timeout_transition(self, now_ms: int) -> "GamePieceStateManager":
        return self.execute_timeout_state_transition(now_ms)
    
    def _handle_state_specific_updates(self, now_ms: int) -> "GamePieceStateManager":
        return self.handle_automatic_state_transitions(now_ms)
    
    def get_command(self) -> Command:
        return self.retrieve_active_command()


class ChessPieceStateFactory:
    """Self-documenting factory for creating different types of chess piece states."""
    
    @staticmethod
    def build_rest_state_with_specific_duration(idle_state: "GamePieceStateManager", movement_rules: Moves, 
                                              visual_renderer: Graphics, movement_physics: Physics, 
                                              state_identifier: str, rest_duration_ms: int) -> "GamePieceStateManager":
        """Create a rest state with specified duration that transitions back to idle."""
        rest_state = GamePieceStateManager(movement_rules, visual_renderer, movement_physics, state_identifier)
        rest_state.requires_rest_period = True
        rest_state.rest_period_duration_ms = rest_duration_ms
        rest_state.configure_state_transition_rule("timeout", idle_state)
        return rest_state

    @staticmethod
    def build_long_duration_rest_state(idle_state: "GamePieceStateManager", movement_rules: Moves, 
                                     visual_renderer: Graphics, movement_physics: Physics) -> "GamePieceStateManager":
        """Create a 2-second rest state that transitions back to idle."""
        return ChessPieceStateFactory.build_rest_state_with_specific_duration(
            idle_state, movement_rules, visual_renderer, movement_physics, "long_rest", 2000)

    @staticmethod
    def build_short_duration_rest_state(idle_state: "GamePieceStateManager", movement_rules: Moves, 
                                       visual_renderer: Graphics, movement_physics: Physics) -> "GamePieceStateManager":
        """Create a 1-second rest state that transitions back to idle."""
        return ChessPieceStateFactory.build_rest_state_with_specific_duration(
            idle_state, movement_rules, visual_renderer, movement_physics, "short_rest", 1000)

    @staticmethod
    def build_movement_state_with_rest_transition(idle_state: "GamePieceStateManager", movement_rules: Moves, 
                                                visual_renderer: Graphics, movement_physics: Physics) -> "GamePieceStateManager":
        """Create a move state that transitions to long rest upon completion."""
        long_rest_state = ChessPieceStateFactory.build_long_duration_rest_state(
            idle_state, movement_rules, visual_renderer, movement_physics)
        move_state = GamePieceStateManager(movement_rules, visual_renderer, movement_physics, "move")
        move_state.configure_state_transition_rule("complete", long_rest_state)
        return move_state


# Complete backward compatibility aliases
State = GamePieceStateManager
StateFactory = ChessPieceStateFactory
PathUtils = GamePieceSpritesPathManager

# Individual function aliases
StateFactory.create_rest_state = ChessPieceStateFactory.build_rest_state_with_specific_duration
StateFactory.create_long_rest_state = ChessPieceStateFactory.build_long_duration_rest_state
StateFactory.create_short_rest_state = ChessPieceStateFactory.build_short_duration_rest_state
StateFactory.create_move_state = ChessPieceStateFactory.build_movement_state_with_rest_transition

# Global function aliases for backward compatibility
def create_long_rest_state(idle_state: "GamePieceStateManager", moves: Moves, graphics: Graphics, physics: Physics) -> "GamePieceStateManager":
    """Create a 2-second rest state that transitions back to idle."""
    return ChessPieceStateFactory.build_long_duration_rest_state(idle_state, moves, graphics, physics)

def create_short_rest_state(idle_state: "GamePieceStateManager", moves: Moves, graphics: Graphics, physics: Physics) -> "GamePieceStateManager":
    """Create a 1-second rest state that transitions back to idle."""
    return ChessPieceStateFactory.build_short_duration_rest_state(idle_state, moves, graphics, physics)

def create_move_state(idle_state: "GamePieceStateManager", moves: Moves, graphics: Graphics, physics: Physics) -> "GamePieceStateManager":
    """Create a move state that transitions to long rest upon completion."""
    return ChessPieceStateFactory.build_movement_state_with_rest_transition(idle_state, moves, graphics, physics)
