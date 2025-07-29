#!/usr/bin/env python3
"""
🎮 GameUI - Compact User Interface for Game
"""
import pygame
import time
from typing import Dict, List


class GameUI:
    """Compact user interface with simple design"""
    
    def __init__(self, panel_width: int = 300):  # Increased from 250 to 300
        self.panel_width = panel_width
        
        # Create simple fonts - larger sizes!
        pygame.font.init()
        self.fonts = {
            'title': pygame.font.Font(None, 28),     # Was 24
            'normal': pygame.font.Font(None, 24),    # Was 20  
            'small': pygame.font.Font(None, 20)      # Was 16
        }
        
        # Simple colors
        self.colors = {
            'bg': (40, 40, 40),
            'white': (255, 255, 255),
            'gray': (150, 150, 150),
            'blue': (100, 150, 255),
            'red': (255, 100, 100),
            'yellow': (255, 255, 0)
        }
    
    def draw_player_panels(self, screen, board_width, window_height, pieces, selection, start_time, score_mgr=None, move_logger=None):
        """Draw player panels"""
        # Left panel - Player A
        self._draw_panel(screen, 0, 0, "A", self.colors['blue'], pieces, selection, start_time, score_mgr, move_logger)
        
        # Right panel - Player B  
        self._draw_panel(screen, self.panel_width + board_width, 0, "B", self.colors['red'], pieces, selection, start_time, score_mgr, move_logger)
    
    def _draw_panel(self, screen, x, y, player, color, pieces, selection, start_time, score_mgr, move_logger):
        """Draw single panel"""
        # Background
        pygame.draw.rect(screen, self.colors['bg'], (x, y, self.panel_width, screen.get_height()))
        
        y_pos = y + 10
        
        # Player title
        title = self.fonts['title'].render(f"Player {player}", True, color)
        screen.blit(title, (x + 10, y_pos))
        y_pos += 35  # Increased from 30 to 35
        
        # Time
        duration = int(time.time() - start_time)
        time_text = f"{duration//60:02d}:{duration%60:02d}"
        time_surf = self.fonts['small'].render(time_text, True, self.colors['gray'])
        screen.blit(time_surf, (x + 10, y_pos))
        y_pos += 28  # Increased from 25 to 28
        
        # Pieces
        player_pieces = self._get_player_pieces(pieces, player)
        pieces_text = f"Pieces: {len(player_pieces)}"
        pieces_surf = self.fonts['normal'].render(pieces_text, True, self.colors['white'])
        screen.blit(pieces_surf, (x + 10, y_pos))
        y_pos += 28  # Increased from 25 to 28
        
        # Score
        if score_mgr:
            try:
                score = score_mgr.get_player_score(player)
                score_surf = self.fonts['normal'].render(f"Score: {score}", True, self.colors['white'])
                screen.blit(score_surf, (x + 10, y_pos))
                y_pos += 25
            except:
                pass
        
        # Selected piece
        selected = selection.get(player, {}).get('selected') if selection else None
        if selected:
            sel_surf = self.fonts['small'].render("Selected:", True, self.colors['yellow'])
            screen.blit(sel_surf, (x + 10, y_pos))
            y_pos += 20
            
            piece_surf = self.fonts['small'].render(selected.piece_id[-4:], True, self.colors['white'])
            screen.blit(piece_surf, (x + 15, y_pos))
            y_pos += 25
        
        # Compact pieces table
        y_pos = self._draw_pieces_mini_table(screen, x, y_pos, player_pieces)
        
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
        """Compact pieces table - by type and count"""
        title_surf = self.fonts['small'].render("My Pieces:", True, self.colors['gray'])
        screen.blit(title_surf, (x + 10, y))
        y += 22
        
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
        
        # Display pieces by importance order with counts
        for piece_type in ['K', 'Q', 'R', 'B', 'N', 'P']:
            if piece_type in piece_counts:
                count = piece_counts[piece_type]
                name = piece_names.get(piece_type, piece_type)
                
                # Format: "King: 1" or "Pawns: 8"
                if count == 1:
                    text = f"{name}: {count}"
                else:
                    # Add s for plurals in English
                    plural_name = name + "s" if name.endswith(('h', 's', 'x')) else name + "s"
                    if name == "Knight":
                        plural_name = "Knights"
                    elif name == "Bishop":
                        plural_name = "Bishops"
                    text = f"{plural_name}: {count}"
                
                surf = self.fonts['small'].render(text, True, self.colors['white'])
                screen.blit(surf, (x + 10, y))
                y += 18
        
        # Total pieces
        total = len(pieces)
        total_surf = self.fonts['small'].render(f"Total: {total}", True, self.colors['gray'])
        screen.blit(total_surf, (x + 10, y))
        y += 25
        
        return y
    
    def _draw_moves_mini(self, screen, x, y, player, move_logger):
        """Recent moves compact"""
        title_surf = self.fonts['small'].render("Recent Moves:", True, self.colors['gray'])
        screen.blit(title_surf, (x + 10, y))
        y += 22
        
        try:
            moves = move_logger.get_recent_moves_for_player(player)[-3:]  # Only 3 moves because they're longer
            for move in moves:
                # Smart truncation by new panel length
                if len(move) > 35:  # Increased the limit
                    # Smart truncation - keep time, piece name and positions
                    if "→" in move:
                        parts = move.split("→")
                        if len(parts) == 2:
                            left_part = parts[0]  # Time + name + start position
                            right_part = parts[1]  # End position
                            if len(left_part) > 20:
                                left_part = left_part[:17] + ".."
                            move_text = left_part + "→" + right_part
                        else:
                            move_text = move[:32] + "..."
                    else:
                        move_text = move[:32] + "..."
                else:
                    move_text = move
                
                surf = self.fonts['small'].render(move_text, True, self.colors['white'])
                screen.blit(surf, (x + 10, y))
                y += 20  # Larger spacing because moves are more detailed
            
            if not moves:
                no_moves_surf = self.fonts['small'].render("No moves yet", True, self.colors['gray'])
                screen.blit(no_moves_surf, (x + 10, y))
        except:
            pass
