#!/usr/bin/env python3
"""
Pawn Promotion UI Manager
========================

Manages the popup interface for pawn promotion selection.
"""

import pygame
from typing import Dict, List, Tuple, Optional, NamedTuple


class PopupDimensions(NamedTuple):
    """Container for popup layout dimensions."""
    width: int
    height: int
    x: int
    y: int


class OptionLayout(NamedTuple):
    """Container for option layout settings."""
    start_y: int
    height: int
    spacing: int
    margin: int


class PromotionUI:
    """Manages the pawn promotion popup interface."""
    
    # Layout constants
    POPUP_WIDTH = 400
    POPUP_HEIGHT = 300
    OPTION_HEIGHT = 30
    OPTION_SPACING = 5
    OPTION_MARGIN = 20
    OVERLAY_ALPHA = 180
    
    # Position constants
    TITLE_Y_OFFSET = 20
    SUBTITLE_Y_OFFSET = 70
    OPTIONS_Y_OFFSET = 110
    INSTRUCTIONS_Y_OFFSET = 40
    
    def __init__(self, screen_width: int, screen_height: int):
        """Initialize the promotion UI manager."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        
        # Pre-calculate popup dimensions
        self.popup_dimensions = self._calculate_popup_dimensions()
        self.option_layout = self._calculate_option_layout()
        
        # Initialize color scheme
        self.colors = self._initialize_colors()
        
        # Initialize content mappings
        self.piece_names = self._initialize_piece_names()
        self.instructions = self._initialize_instructions()
    
    def _calculate_popup_dimensions(self) -> PopupDimensions:
        """Calculate popup position and dimensions."""
        x = (self.screen_width - self.POPUP_WIDTH) // 2
        y = (self.screen_height - self.POPUP_HEIGHT) // 2
        return PopupDimensions(self.POPUP_WIDTH, self.POPUP_HEIGHT, x, y)
    
    def _calculate_option_layout(self) -> OptionLayout:
        """Calculate option layout settings."""
        start_y = self.popup_dimensions.y + self.OPTIONS_Y_OFFSET
        return OptionLayout(
            start_y, self.OPTION_HEIGHT, 
            self.OPTION_SPACING, self.OPTION_MARGIN
        )
    
    def _initialize_colors(self) -> Dict[str, Tuple[int, ...]]:
        """Initialize color scheme."""
        return {
            'background': (0, 0, 0, self.OVERLAY_ALPHA),
            'popup_bg': (255, 255, 255),
            'border': (100, 100, 100),
            'text': (0, 0, 0),
            'selected': (0, 150, 255),
            'selected_text': (255, 255, 255),
            'option_bg': (240, 240, 240),
            'player_a': (255, 0, 0),
            'player_b': (0, 0, 255)
        }
    
    def _initialize_piece_names(self) -> Dict[str, str]:
        """Initialize piece name mappings."""
        return {
            'Q': 'Queen',
            'R': 'Rook', 
            'B': 'Bishop',
            'N': 'Knight'
        }
    
    def _initialize_instructions(self) -> Dict[str, str]:
        """Initialize player instruction mappings."""
        return {
            'A': "Player A: Use Arrow Keys to navigate, ENTER to select",
            'B': "Player B: Use WASD to navigate, SPACE to select"
        }
    
    def draw_promotion_popup(self, surface: pygame.Surface, player: str, 
                           selected_option: int, options: List[str]) -> None:
        """Draw the promotion selection popup."""
        self._draw_overlay(surface)
        self._draw_popup_background(surface)
        
        player_color = self._get_player_color(player)
        
        self._draw_title(surface, player, player_color)
        self._draw_subtitle(surface)
        self._draw_options(surface, options, selected_option, player_color)
        self._draw_instructions(surface, player)
    
    def _draw_overlay(self, surface: pygame.Surface):
        """Draw semi-transparent overlay."""
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(self.OVERLAY_ALPHA)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
    
    def _draw_popup_background(self, surface: pygame.Surface):
        """Draw popup background and border."""
        popup_rect = pygame.Rect(
            self.popup_dimensions.x, self.popup_dimensions.y,
            self.popup_dimensions.width, self.popup_dimensions.height
        )
        pygame.draw.rect(surface, self.colors['popup_bg'], popup_rect)
        pygame.draw.rect(surface, self.colors['border'], popup_rect, 3)
    
    def _get_player_color(self, player: str) -> Tuple[int, int, int]:
        """Get color for the specified player."""
        return self.colors['player_a'] if player == 'A' else self.colors['player_b']
    
    def _draw_title(self, surface: pygame.Surface, player: str, player_color: Tuple[int, int, int]):
        """Draw the popup title."""
        title_text = f"Player {player} - Pawn Promotion!"
        title_surface = self.title_font.render(title_text, True, player_color)
        title_x = self.popup_dimensions.x + (self.popup_dimensions.width - title_surface.get_width()) // 2
        title_y = self.popup_dimensions.y + self.TITLE_Y_OFFSET
        surface.blit(title_surface, (title_x, title_y))
    
    def _draw_subtitle(self, surface: pygame.Surface):
        """Draw the popup subtitle."""
        subtitle_text = "Choose your new piece:"
        subtitle_surface = self.font.render(subtitle_text, True, self.colors['text'])
        subtitle_x = self.popup_dimensions.x + (self.popup_dimensions.width - subtitle_surface.get_width()) // 2
        subtitle_y = self.popup_dimensions.y + self.SUBTITLE_Y_OFFSET
        surface.blit(subtitle_surface, (subtitle_x, subtitle_y))
    
    def _draw_options(self, surface: pygame.Surface, options: List[str], 
                     selected_option: int, player_color: Tuple[int, int, int]):
        """Draw the selectable options."""
        for i, option in enumerate(options):
            option_rect = self._calculate_option_rect(i)
            self._draw_single_option(surface, option_rect, option, i == selected_option, player_color)
    
    def _calculate_option_rect(self, index: int) -> pygame.Rect:
        """Calculate rectangle for a specific option."""
        option_y = self.option_layout.start_y + index * (self.option_layout.height + self.option_layout.spacing)
        return pygame.Rect(
            self.popup_dimensions.x + self.option_layout.margin,
            option_y,
            self.popup_dimensions.width - 2 * self.option_layout.margin,
            self.option_layout.height
        )
    
    def _draw_single_option(self, surface: pygame.Surface, option_rect: pygame.Rect, 
                           option: str, is_selected: bool, player_color: Tuple[int, int, int]):
        """Draw a single option with appropriate styling."""
        # Draw background and border
        if is_selected:
            pygame.draw.rect(surface, self.colors['selected'], option_rect)
            pygame.draw.rect(surface, player_color, option_rect, 2)
            text_color = self.colors['selected_text']
        else:
            pygame.draw.rect(surface, self.colors['option_bg'], option_rect)
            pygame.draw.rect(surface, self.colors['border'], option_rect, 1)
            text_color = self.colors['text']
        
        # Draw option text
        self._draw_option_text(surface, option_rect, option, text_color)
    
    def _draw_option_text(self, surface: pygame.Surface, option_rect: pygame.Rect, 
                         option: str, text_color: Tuple[int, int, int]):
        """Draw text for an option."""
        option_text = self.piece_names.get(option, option)
        text_surface = self.font.render(option_text, True, text_color)
        text_x = option_rect.x + 10
        text_y = option_rect.y + (option_rect.height - text_surface.get_height()) // 2
        surface.blit(text_surface, (text_x, text_y))
    
    def _draw_instructions(self, surface: pygame.Surface, player: str):
        """Draw player instructions."""
        instruction_text = self.instructions[player]
        instruction_surface = self.font.render(instruction_text, True, self.colors['text'])
        instruction_x = self.popup_dimensions.x + (self.popup_dimensions.width - instruction_surface.get_width()) // 2
        instruction_y = self.popup_dimensions.y + self.popup_dimensions.height - self.INSTRUCTIONS_Y_OFFSET
        surface.blit(instruction_surface, (instruction_x, instruction_y))
    
    def get_popup_bounds(self) -> Tuple[int, int, int, int]:
        """Get the bounds of the promotion popup (x, y, width, height)."""
        return (
            self.popup_dimensions.x, self.popup_dimensions.y,
            self.popup_dimensions.width, self.popup_dimensions.height
        )
    
    def is_point_in_popup(self, x: int, y: int) -> bool:
        """Check if a point is inside the popup area."""
        return (self.popup_dimensions.x <= x <= self.popup_dimensions.x + self.popup_dimensions.width and
                self.popup_dimensions.y <= y <= self.popup_dimensions.y + self.popup_dimensions.height)
    
    def get_option_at_point(self, x: int, y: int, num_options: int) -> Optional[int]:
        """Get the option index at a specific point, or None if not over an option."""
        if not self.is_point_in_popup(x, y):
            return None
            
        for i in range(num_options):
            option_rect = self._calculate_option_rect(i)
            if option_rect.collidepoint(x, y):
                return i
        return None
