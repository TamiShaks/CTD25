#!/usr/bin/env python3
"""
# GameUI - Compact User Interface for Game
"""
import pygame
import time
from typing import Dict, List


class GameUI:
    """Compact user interface with simple design"""
    
    def __init__(self, panel_width: int = 300):
        """Initialize the UI with professional styling."""
        self.panel_width = panel_width
        
        # Set up professional fonts
        pygame.font.init()
        try:
            self.fonts = {
                'title': pygame.font.SysFont('bahnschrift', 20, bold=True),
                'normal': pygame.font.SysFont('bahnschrift', 18),
                'small': pygame.font.SysFont('bahnschrift', 16)
            }
        except:
            self.fonts = {
                'title': pygame.font.Font(None, 20),
                'normal': pygame.font.Font(None, 18),
                'small': pygame.font.Font(None, 16)
            }

        # Modern color scheme with high contrast
        self.colors = {
            'bg': (245, 245, 245),         # Light background
            'white': (255, 255, 255),      # Pure white
            'gray': (100, 100, 100),       # Dark gray
            'blue': (50, 120, 255),        # Modern blue
            'red': (255, 80, 80),          # Modern red
            'yellow': (240, 200, 80),      # Pleasant yellow
            'border': (180, 180, 180),     # Soft border
            'section': (230, 230, 230),    # Section background
            'text': (30, 30, 30)           # Dark text
        }

    def draw_player_panels(self, screen, board_width, window_height, pieces, selection, start_time, score_mgr=None, move_logger=None):
        """Draw player panels"""
        # Left panel - Player A
        self._draw_panel(screen, 0, 0, "A", self.colors['blue'], pieces, selection, start_time, score_mgr, move_logger)
        
        # Right panel - Player B  
        self._draw_panel(screen, self.panel_width + board_width, 0, "B", self.colors['red'], pieces, selection, start_time, score_mgr, move_logger)
    
    def _draw_panel(self, screen, x, y, player, color, pieces, selection, start_time, score_mgr, move_logger):
        """Draw single panel with professional styling."""
        # Panel background with border
        pygame.draw.rect(screen, self.colors['border'], (x, y, self.panel_width, screen.get_height()))
        pygame.draw.rect(screen, self.colors['bg'], (x+2, y+2, self.panel_width-4, screen.get_height()-4))
        
        y_pos = y + 15
        
        # Player header section with background
        header_height = 50
        pygame.draw.rect(screen, self.colors['section'], (x+5, y_pos, self.panel_width-10, header_height))
        pygame.draw.rect(screen, self.colors['border'], (x+5, y_pos, self.panel_width-10, header_height), 1)
        
        # Player title - centered with glow effect
        title_shadow = self.fonts['title'].render(f"Player {player}", True, self.colors['border'])
        title = self.fonts['title'].render(f"Player {player}", True, color)
        title_x = x + (self.panel_width - title.get_width()) // 2
        screen.blit(title_shadow, (title_x + 1, y_pos + 9))
        screen.blit(title, (title_x, y_pos + 8))
        
        # Time - centered with subtle shadow
        duration = int(time.time() - start_time)
        time_text = f"Time: {duration//60:02d}:{duration%60:02d}"
        time_shadow = self.fonts['normal'].render(time_text, True, self.colors['border'])
        time_surf = self.fonts['normal'].render(time_text, True, self.colors['text'])
        time_x = x + (self.panel_width - time_surf.get_width()) // 2
        screen.blit(time_surf, (time_x, y_pos + 28))
        
        y_pos += header_height + 15
        
        # Score (if available)
        if score_mgr:
            try:
                score = score_mgr.get_player_score(player)
                score_surf = self.fonts['normal'].render(f"Score: {score}", True, self.colors['text'])
                screen.blit(score_surf, (x + 10, y_pos))
                y_pos += 25
            except:
                pass
        
        # Selected piece
        selected = selection.get(player, {}).get('selected') if selection else None
        if selected:
            sel_surf = self.fonts['normal'].render("Selected Piece:", True, self.colors['text'])
            screen.blit(sel_surf, (x + 10, y_pos))
            y_pos += 25
            
            piece_surf = self.fonts['normal'].render(selected.piece_id[-4:], True, color)
            piece_x = x + (self.panel_width - piece_surf.get_width()) // 2
            screen.blit(piece_surf, (piece_x, y_pos))
            y_pos += 35
        
        # Recent moves
        if move_logger:
            y_pos += 15
            self._draw_moves_mini(screen, x, y_pos, player, move_logger)
    
    def _get_player_pieces(self, pieces, player):
        """Get pieces by player"""
        player_pieces = []
        
        for piece_id, piece in pieces.items():
            if len(piece.piece_id) >= 2:
                color_char = piece.piece_id[1]
                if (player == "A" and color_char == "W") or (player == "B" and color_char == "B"):
                    player_pieces.append(piece)
        
        return player_pieces
    
    def _draw_pieces_mini_table(self, screen, x, y, pieces):
        """Draw pieces table with borders and professional styling."""
        # Section title with background
        title_height = 30
        title_width = self.panel_width - 20
        pygame.draw.rect(screen, self.colors['section'], (x+10, y, title_width, title_height))
        pygame.draw.rect(screen, self.colors['border'], (x+10, y, title_width, title_height), 1)
        
        title_surf = self.fonts['normal'].render("Active Pieces", True, self.colors['white'])
        title_x = x + (self.panel_width - title_surf.get_width()) // 2
        screen.blit(title_surf, (title_x, y + 5))
        y += title_height + 5
        
        # Table background
        table_height = 150
        pygame.draw.rect(screen, self.colors['section'], (x+10, y, title_width, table_height))
        pygame.draw.rect(screen, self.colors['border'], (x+10, y, title_width, table_height), 1)
        
        # Count pieces by type
        piece_counts = {}
        piece_names = {
            'K': 'King',
            'Q': 'Queen', 
            'R': 'Rook',
            'B': 'Bishop',
            'N': 'Knight',
            'P': 'Pawn'
        }
        
        for piece in pieces:
            piece_type = piece.piece_id[0] if piece.piece_id else '?'
            piece_counts[piece_type] = piece_counts.get(piece_type, 0) + 1
        
        # Display pieces in table format
        y += 10
        col_width = title_width // 2
        row_height = 22
        
        for i, piece_type in enumerate(['K', 'Q', 'R', 'B', 'N', 'P']):
            if piece_type in piece_counts:
                count = piece_counts[piece_type]
                name = piece_names.get(piece_type, piece_type)
                
                # Format piece name and count
                if count == 1:
                    text = f"{name}"
                else:
                    plural_name = name + "s" if name.endswith(('h', 's', 'x')) else name + "s"
                    if name == "Knight":
                        plural_name = "Knights"
                    elif name == "Bishop":
                        plural_name = "Bishops"
                    text = f"{plural_name}"
                
                # Draw piece name
                name_surf = self.fonts['small'].render(text, True, self.colors['white'])
                screen.blit(name_surf, (x + 20, y + (i * row_height)))
                
                # Draw count with right alignment
                count_text = str(count)
                count_surf = self.fonts['small'].render(count_text, True, self.colors['gray'])
                count_x = x + col_width + (col_width - count_surf.get_width()) - 20
                screen.blit(count_surf, (count_x, y + (i * row_height)))
        
        # Draw horizontal separator
        sep_y = y + (6 * row_height)
        pygame.draw.line(screen, self.colors['border'], 
                        (x+20, sep_y), 
                        (x+title_width-10, sep_y))
        
        # Total pieces with right alignment
        total = len(pieces)
        total_text = "Total Pieces"
        total_label = self.fonts['normal'].render(total_text, True, self.colors['white'])
        total_count = self.fonts['normal'].render(str(total), True, self.colors['gray'])
        
        screen.blit(total_label, (x + 20, sep_y + 10))
        total_x = x + col_width + (col_width - total_count.get_width()) - 20
        screen.blit(total_count, (total_x, sep_y + 10))
        
        return sep_y + 40
    
    def _draw_moves_mini(self, screen, x, y, player, move_logger):
        """Draw recent moves with enhanced styling."""
        # Section title with background
        title_height = 40
        title_width = self.panel_width - 20
        
        # Title background with gradient effect
        for i in range(title_height):
            alpha = 255 - (i * 2)
            current_color = (
                self.colors['section'][0],
                self.colors['section'][1],
                self.colors['section'][2]
            )
            pygame.draw.rect(screen, current_color, (x+10, y+i, title_width, 1))
            
        pygame.draw.rect(screen, self.colors['border'], (x+10, y, title_width, title_height), 2)
        
        # Title with shadow effect
        shadow_offset = 1
        title_shadow = self.fonts['title'].render("Recent Moves", True, self.colors['gray'])
        title = self.fonts['title'].render("Recent Moves", True, self.colors['text'])
        
        title_x = x + (self.panel_width - title.get_width()) // 2
        screen.blit(title_shadow, (title_x + shadow_offset, y + 5 + shadow_offset))
        screen.blit(title, (title_x, y + 5))
        y += title_height + 5
        
        # Moves list background - taller for better visibility
        moves_height = 200
        pygame.draw.rect(screen, self.colors['white'], (x+10, y, title_width, moves_height))
        pygame.draw.rect(screen, self.colors['border'], (x+10, y, title_width, moves_height), 2)
        
        try:
            # Show more moves
            moves = move_logger.get_recent_moves_for_player(player)[-5:]  # Show last 5 moves
            if moves:
                y += 15  # More padding at top
                for i, move in enumerate(moves):
                    # Move number badge
                    move_num = len(moves) - i
                    badge_color = self.colors['blue'] if player == 'A' else self.colors['red']
                    pygame.draw.circle(screen, badge_color, (x + 30, y + 10), 12)
                    num_surf = self.fonts['small'].render(str(move_num), True, self.colors['white'])
                    num_x = x + 30 - num_surf.get_width()//2
                    num_y = y + 10 - num_surf.get_height()//2
                    screen.blit(num_surf, (num_x, num_y))
                    
                    # Smart move text formatting
                    if len(move) > 35:
                        if "→" in move:
                            parts = move.split("→")
                            if len(parts) == 2:
                                left_part = parts[0].strip()
                                right_part = parts[1].strip()
                                
                                # Format time separately
                                time_part = left_part[:8] if len(left_part) >= 8 else ""
                                move_part = left_part[8:] if len(left_part) >= 8 else left_part
                                
                                # Draw time in gray
                                if time_part:
                                    time_surf = self.fonts['small'].render(time_part, True, self.colors['gray'])
                                    screen.blit(time_surf, (x + 50, y))
                                
                                # Draw move with arrow
                                if len(move_part) > 12:
                                    move_part = move_part[:10] + ".."
                                move_text = f"{move_part} ⟹ {right_part}"
                            else:
                                move_text = move[:32] + "..."
                        else:
                            move_text = move[:32] + "..."
                    else:
                        move_text = move
                    
                    # Draw move text with shadow effect
                    shadow_surf = self.fonts['normal'].render(move_text, True, self.colors['gray'])
                    move_surf = self.fonts['normal'].render(move_text, True, self.colors['text'])
                    
                    text_x = x + (70 if ":" in move else 25)
                    screen.blit(shadow_surf, (text_x + 1, y + 1))
                    screen.blit(move_surf, (text_x, y))
                    
                    # Add minimal separator with darker color for dark theme
                    if i < len(moves) - 1:
                        sep_y = y + 18
                        pygame.draw.line(screen, self.colors['border'],
                                      (x + 10, sep_y),
                                      (x + title_width - 10, sep_y), 1)
                    
                    y += 25  # Reduced space between moves
            else:
                # No moves message - centered with style
                no_moves_surf = self.fonts['title'].render("No moves yet", True, self.colors['gray'])
                no_moves_x = x + (title_width - no_moves_surf.get_width()) // 2
                no_moves_y = y + (moves_height - no_moves_surf.get_height()) // 2
                
                # Draw with shadow effect
                shadow_surf = self.fonts['title'].render("No moves yet", True, (220, 220, 220))
                screen.blit(shadow_surf, (no_moves_x + 1, no_moves_y + 1))
                screen.blit(no_moves_surf, (no_moves_x, no_moves_y))
        except:
            # Error message - centered
            error_surf = self.fonts['small'].render("Move history unavailable", True, self.colors['gray'])
            error_x = x + (title_width - error_surf.get_width()) // 2
            error_y = y + (moves_height - error_surf.get_height()) // 2
            screen.blit(error_surf, (error_x, error_y))
