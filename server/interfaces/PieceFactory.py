import pathlib
from typing import Dict, Tuple
import json
from Board import Board
from GraphicsFactory import GraphicsFactory
from Moves import Moves
from PhysicsFactory import PhysicsFactory
from Piece import Piece
from State import State

class PieceFactory:
    """Creates chess pieces with complete state machines from filesystem structure."""
    
    def __init__(self, board: Board, pieces_root: pathlib.Path):
        self.board = board
        self.pieces_root = pieces_root
        self.graphics_factory = GraphicsFactory()
        self.physics_factory = PhysicsFactory(board)
        self.piece_templates: Dict[str, Dict[str, State]] = {}
        self.build_all_piece_templates()
    
    def build_all_piece_templates(self):
        if not self.pieces_root.exists():
            print(f"Warning: Pieces directory {self.pieces_root} does not exist")
            return
            
        for piece_directory in self.pieces_root.iterdir():
            if piece_directory.is_dir():
                piece_type = piece_directory.name
                try:
                    complete_state_machine = self.build_state_machine_for_piece(piece_directory)
                    self.piece_templates[piece_type] = complete_state_machine
                    print(f"✓ Built {piece_type} with {len(complete_state_machine)} states")
                except Exception as error:
                    print(f"✗ Failed to build {piece_type}: {error}")

    def build_state_machine_for_piece(self, piece_directory: pathlib.Path) -> Dict[str, State]:
        movement_rules = self.load_movement_rules_from_file(piece_directory)
        piece_configuration = self.load_piece_configuration_from_file(piece_directory)
        
        discovered_states = self.discover_existing_states(piece_directory, movement_rules, piece_configuration)
        self.create_any_missing_essential_states(piece_directory, discovered_states, movement_rules, piece_configuration)
        self.connect_all_state_transitions(discovered_states)
        
        return discovered_states
    
    def load_movement_rules_from_file(self, piece_directory: pathlib.Path) -> Moves:
        moves_file = piece_directory / "moves.txt"
        return Moves(moves_file, (self.board.H_cells, self.board.W_cells))
    
    def load_piece_configuration_from_file(self, piece_directory: pathlib.Path) -> dict:
        config_file = piece_directory / "config.json"
        if not config_file.exists():
            return {}
        try:
            with open(config_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as error:
            print(f"Warning: Invalid config.json for {piece_directory.name}: {error}")
            return {}
    
    def discover_existing_states(self, piece_directory: pathlib.Path, movement_rules: Moves, config: dict) -> Dict[str, State]:
        states_directory = piece_directory / "states"
        found_states = {}
        
        if not (states_directory.exists() and states_directory.is_dir()):
            return found_states
            
        for state_directory in states_directory.iterdir():
            if state_directory.is_dir():
                state_name = state_directory.name
                state_object = self.create_state_from_directory(state_directory, state_name, movement_rules, config)
                found_states[state_name] = state_object
                
        return found_states
    
    def create_state_from_directory(self, state_directory: pathlib.Path, state_name: str, movement_rules: Moves, config: dict) -> State:
        sprites_directory = state_directory / "sprites"
        graphics = self.graphics_factory.create(
            sprites_directory, 
            config.get(state_name, {}), 
            (self.board.cell_W_pix, self.board.cell_H_pix),
            state_name
        )
        
        physics = self.physics_factory.create((0, 0), config.get(state_name, {}))
        state = State(movement_rules, graphics, physics, state_name)
        self.apply_special_state_properties(state, state_name)
        return state
    
    def apply_special_state_properties(self, state: State, state_name: str):
        rest_timing_config = {
            "long_rest": (True, 3000),
            "short_rest": (True, 2000),
            "jump": (True, 1500)
        }
        
        if state_name in rest_timing_config:
            is_rest, duration_ms = rest_timing_config[state_name]
            state.is_rest_state = is_rest
            state.rest_duration_ms = duration_ms
    
    def create_any_missing_essential_states(self, piece_directory: pathlib.Path, existing_states: Dict[str, State], movement_rules: Moves, config: dict):
        essential_states = ["idle", "move", "long_rest"]
        missing_states = [state for state in essential_states if state not in existing_states]
        
        for missing_state_name in missing_states:
            fallback_state = self.create_state_with_fallback_graphics(piece_directory, missing_state_name, movement_rules, config)
            existing_states[missing_state_name] = fallback_state
    
    def create_state_with_fallback_graphics(self, piece_directory: pathlib.Path, state_name: str, movement_rules: Moves, config: dict) -> State:
        state_specific_sprites = piece_directory / "states" / state_name / "sprites"
        fallback_sprites = piece_directory / "sprites"
        sprites_directory = state_specific_sprites if state_specific_sprites.exists() else fallback_sprites
        
        graphics = self.graphics_factory.create(
            sprites_directory,
            config.get(state_name, {}),
            (self.board.cell_W_pix, self.board.cell_H_pix),
            state_name
        )
        
        physics = self.physics_factory.create((0, 0), config.get(state_name, {}))
        state = State(movement_rules, graphics, physics, state_name)
        self.apply_special_state_properties(state, state_name)
        return state

    def connect_all_state_transitions(self, states: Dict[str, State]):
        transition_rules = [
            ("idle", "Move", "move"),
            ("idle", "Jump", "jump"), 
            ("idle", "Attack", "attack"),
            ("move", "complete", "long_rest"),
            ("move", "complete", "idle"),
            ("jump", "complete", "short_rest"),
            ("jump", "timeout", "short_rest"),
            ("jump", "complete", "idle"),
            ("jump", "timeout", "idle"),
            ("attack", "complete", "idle"),
            ("long_rest", "timeout", "idle"),
            ("short_rest", "timeout", "idle")
        ]
        
        for from_state, event_trigger, to_state in transition_rules:
            self.create_transition_if_both_states_exist(states, from_state, event_trigger, to_state)
    
    def create_transition_if_both_states_exist(self, states: Dict[str, State], from_state: str, event_trigger: str, to_state: str):
        if from_state in states and to_state in states:
            states[from_state].set_transition(event_trigger, states[to_state])

    def create_piece(self, piece_type: str, board_position: Tuple[int, int]) -> Piece:
        if piece_type not in self.piece_templates:
            available_types = list(self.piece_templates.keys())
            raise ValueError(f"Unknown piece type: {piece_type}. Available: {available_types}")
        
        template_states = self.piece_templates[piece_type]
        independent_states = self.clone_template_states_for_new_piece(piece_type, template_states, board_position)
        self.clone_template_transitions_for_new_piece(template_states, independent_states)
        
        initial_state = independent_states.get("idle", list(independent_states.values())[0])
        unique_piece_id = self.generate_unique_piece_id(piece_type, board_position, initial_state)
        
        return Piece(unique_piece_id, initial_state, piece_type)
    
    def clone_template_states_for_new_piece(self, piece_type: str, template_states: Dict[str, State], board_position: Tuple[int, int]) -> Dict[str, State]:
        independent_states = {}
        
        for state_name, template_state in template_states.items():
            fresh_graphics = self.create_fresh_graphics_for_piece_instance(piece_type, state_name)
            positioned_physics = self.physics_factory.create(board_position, {})
            
            independent_state = State(template_state.moves, fresh_graphics, positioned_physics, state_name)
            independent_state.is_rest_state = template_state.is_rest_state
            independent_state.rest_duration_ms = template_state.rest_duration_ms
            
            independent_states[state_name] = independent_state
            
        return independent_states
    
    def create_fresh_graphics_for_piece_instance(self, piece_type: str, state_name: str):
        state_specific_sprites = self.pieces_root / piece_type / "states" / state_name / "sprites"
        fallback_sprites = self.pieces_root / piece_type / "sprites"
        sprites_directory = state_specific_sprites if state_specific_sprites.exists() else fallback_sprites
        
        return self.graphics_factory.create(
            sprites_directory,
            {},
            (self.board.cell_W_pix, self.board.cell_H_pix),
            state_name
        )
    
    def clone_template_transitions_for_new_piece(self, template_states: Dict[str, State], independent_states: Dict[str, State]):
        for state_name, template_state in template_states.items():
            if state_name not in independent_states:
                continue
                
            for event_trigger, target_template in template_state.transitions.items():
                target_state_name = target_template.state
                if target_state_name in independent_states:
                    independent_states[state_name].set_transition(event_trigger, independent_states[target_state_name])
    
    def generate_unique_piece_id(self, piece_type: str, board_position: Tuple[int, int], state: State) -> str:
        return f"{piece_type}_{board_position[0]}_{board_position[1]}_{id(state)}"
