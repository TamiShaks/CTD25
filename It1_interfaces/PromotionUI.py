#!/usr/bin/env python3
"""
🎮 Pawn Promotion UI Manager
============================

Manages the popup interface for pawn promotion selection.
"""

import pygame
from typing import Dict, List, Tuple, Optional

class PromotionUI:
    """Manages the pawn promotion popup interface."""
    
    def __init__(self, screen_width: int, screen_height: int):
        """Initialize the promotion UI manager."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        
        # Colors
        self.colors = {
            'background': (0, 0, 0, 180),  # Semi-transparent black
            'popup_bg': (255, 255, 255),
            'border': (100, 100, 100),
            'text': (0, 0, 0),
            'selected': (0, 150, 255),
            'player_a': (255, 0, 0),
            'player_b': (0, 0, 255)
        }
        
        # Piece names for display
        self.piece_names = {
            'Q': 'Queen (מלכה)',
            'R': 'Rook (צריח)', 
            'B': 'Bishop (רץ)',
            'N': 'Knight (פרש)'
        }
        
        # Instructions for each player
        self.instructions = {
            'A': "Player A: Use WASD to navigate, SPACE to select",
            'B': "Player B: Use Arrow Keys to navigate, ENTER to select"
        }
    
    def draw_promotion_popup(self, surface: pygame.Surface, player: str, 
                           selected_option: int, options: List[str]) -> None:
        """Draw the promotion selection popup."""
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Calculate popup dimensions
        popup_width = 400
        popup_height = 300
        popup_x = (self.screen_width - popup_width) // 2
        popup_y = (self.screen_height - popup_height) // 2
        
        # Draw popup background
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
        pygame.draw.rect(surface, self.colors['popup_bg'], popup_rect)
        pygame.draw.rect(surface, self.colors['border'], popup_rect, 3)
        
        # Player color
        player_color = self.colors['player_a'] if player == 'A' else self.colors['player_b']
        
        # Draw title
        title_text = f"Player {player} - Pawn Promotion!"
        title_surface = self.title_font.render(title_text, True, player_color)
        title_x = popup_x + (popup_width - title_surface.get_width()) // 2
        surface.blit(title_surface, (title_x, popup_y + 20))
        
        # Draw subtitle
        subtitle_text = "Choose your new piece:"
        subtitle_surface = self.font.render(subtitle_text, True, self.colors['text'])
        subtitle_x = popup_x + (popup_width - subtitle_surface.get_width()) // 2
        surface.blit(subtitle_surface, (subtitle_x, popup_y + 70))
        
        # Draw options
        option_y_start = popup_y + 110
        option_height = 30
        option_spacing = 5
        
        for i, option in enumerate(options):
            option_y = option_y_start + i * (option_height + option_spacing)
            option_rect = pygame.Rect(popup_x + 20, option_y, popup_width - 40, option_height)
            
            # Highlight selected option
            if i == selected_option:
                pygame.draw.rect(surface, self.colors['selected'], option_rect)
                pygame.draw.rect(surface, player_color, option_rect, 2)
            else:
                pygame.draw.rect(surface, (240, 240, 240), option_rect)
                pygame.draw.rect(surface, self.colors['border'], option_rect, 1)
            
            # Draw option text
            option_text = self.piece_names.get(option, option)
            text_color = (255, 255, 255) if i == selected_option else self.colors['text']
            text_surface = self.font.render(option_text, True, text_color)
            text_x = option_rect.x + 10
            text_y = option_rect.y + (option_height - text_surface.get_height()) // 2
            surface.blit(text_surface, (text_x, text_y))
        
        # Draw instructions
        instruction_text = self.instructions[player]
        instruction_surface = self.font.render(instruction_text, True, self.colors['text'])
        instruction_x = popup_x + (popup_width - instruction_surface.get_width()) // 2
        surface.blit(instruction_surface, (instruction_x, popup_y + popup_height - 40))
    
    def get_popup_bounds(self) -> Tuple[int, int, int, int]:
        """Get the bounds of the promotion popup (x, y, width, height)."""
        popup_width = 400
        popup_height = 300
        popup_x = (self.screen_width - popup_width) // 2
        popup_y = (self.screen_height - popup_height) // 2
        return (popup_x, popup_y, popup_width, popup_height)
