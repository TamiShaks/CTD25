#!/usr/bin/env python3
"""
GameUI - Fullscreen Dark Mode Modern UI for Kung Fu Chess
"""
import pygame
import time

class GameUI:
    """Modern dark-themed user interface with centered board and side panels"""
    
    def __init__(self, panel_width: int = 300):
        pygame.font.init()
        self.panel_width = panel_width

        self.fonts = {
            'title': pygame.font.SysFont('segoe ui semibold', 20, bold=True),
            'normal': pygame.font.SysFont('segoe ui', 18),
            'small': pygame.font.SysFont('segoe ui', 16)
        }

        self.colors = {
            'bg': (20, 20, 20),          # Dark background
            'panel': (30, 30, 30),       # Panel background
            'text': (230, 230, 230),     # Bright text
            'accent': (100, 149, 237),   # Cornflower Blue
            'border': (70, 70, 70),      # Subtle border
            'red': (200, 70, 70),
            'blue': (70, 130, 220)
        }

    def draw_ui(self, screen, board_surface, pieces, selection, start_time):
        screen_width, screen_height = pygame.display.get_surface().get_size()
        board_size = board_surface.get_width()
        board_x = (screen_width - board_size) // 2
        board_y = (screen_height - board_size) // 2

        # Fill background
        screen.fill(self.colors['bg'])

        # Draw panels
        self._draw_panel(screen, 0, 0, "A", self.colors['blue'], selection, start_time)
        self._draw_panel(screen, screen_width - self.panel_width, 0, "B", self.colors['red'], selection, start_time)

        # Draw board in center
        screen.blit(board_surface, (board_x, board_y))

    def _draw_panel(self, screen, x, y, player, color, selection, start_time):
        height = pygame.display.get_surface().get_height()
        pygame.draw.rect(screen, self.colors['panel'], (x, y, self.panel_width, height))
        pygame.draw.rect(screen, self.colors['border'], (x, y, self.panel_width, height), 2)

        y_offset = 30

        title = self.fonts['title'].render(f"Player {player}", True, color)
        title_x = x + (self.panel_width - title.get_width()) // 2
        screen.blit(title, (title_x, y_offset))
        y_offset += 40

        duration = int(time.time() - start_time)
        time_text = f"Time: {duration // 60:02d}:{duration % 60:02d}"
        time_surf = self.fonts['normal'].render(time_text, True, self.colors['text'])
        screen.blit(time_surf, (x + 20, y_offset))
        y_offset += 30

        selected = selection.get(player, {}).get('selected') if selection else None
        if selected:
            sel_surf = self.fonts['normal'].render("Selected:", True, self.colors['text'])
            piece_surf = self.fonts['title'].render(selected.piece_id[-4:], True, color)
            screen.blit(sel_surf, (x + 20, y_offset))
            y_offset += 25
            screen.blit(piece_surf, (x + 20, y_offset))
            y_offset += 35