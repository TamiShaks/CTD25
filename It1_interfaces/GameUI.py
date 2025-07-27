import pygame
import time

class GameUI:
    """Class responsible for drawing the game's user interface panels."""
    
    def __init__(self, info_panel_width=250):
        self.info_panel_width = info_panel_width
        
        # פונטים לטבלת המידע
        self.font_title = pygame.font.Font(None, 26)
        self.font_normal = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 18)
    
    def draw_player_panels(self, screen, board_width, window_height, game_pieces, selection, 
                          start_time, score_manager=None, move_logger=None):
        """Draw separate information panels for each player."""
        # פאנל שחקן A (שמאל) - לבן
        self._draw_player_panel(screen, 'A', 0, window_height, game_pieces, selection, 
                               start_time, score_manager, move_logger)
        
        # פאנל שחקן B (ימין) - שחור
        panel_b_x = self.info_panel_width + board_width
        self._draw_player_panel(screen, 'B', panel_b_x, window_height, game_pieces, selection, 
                               start_time, score_manager, move_logger)

    def _draw_player_panel(self, screen, player, panel_x, window_height, game_pieces, selection, 
                          start_time, score_manager=None, move_logger=None):
        """Draw information panel for a specific player."""
        panel_y = 0
        panel_width = self.info_panel_width
        panel_height = window_height
        
        # קביעת צבעים לפי שחקן
        if player == 'A':
            player_color = "White"
            bg_color = (50, 50, 70)  # כחול כהה לשחקן לבן
            border_color = (100, 100, 150)
            title_color = (255, 255, 255)
            player_symbol = "⚪"
        else:
            player_color = "Black" 
            bg_color = (70, 50, 50)  # אדום כהה לשחקן שחור
            border_color = (150, 100, 100)
            title_color = (255, 255, 255)
            player_symbol = "⚫"
        
        # רקע לפאנל
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, bg_color, panel_rect)
        pygame.draw.rect(screen, border_color, panel_rect, 2)
        
        # כותרת שחקן
        y_offset = 15
        title_text = self.font_title.render(f"{player_symbol} PLAYER {player}", True, title_color)
        screen.blit(title_text, (panel_x + 10, y_offset))
        y_offset += 35
        
        # ניקוד מ-ScoreManager - מידע חשוב ראשון!
        if score_manager:
            scores = score_manager.get_score()
            player_score = scores.get(player_color, 0)
            score_text = self.font_title.render(f"🏆 SCORE: {player_score}", True, (255, 215, 0))
            screen.blit(score_text, (panel_x + 10, y_offset))
            y_offset += 35
        
        # תנועות מ-MoveLogger
        if move_logger:
            # Get all moves and count by player color
            all_moves = move_logger.get_move_history()
            white_moves = len([m for m in all_moves if "W" in m["piece_id"]])
            black_moves = len([m for m in all_moves if "B" in m["piece_id"]])
            player_moves = white_moves if player_color == 'white' else black_moves
            moves_text = self.font_normal.render(f"📝 Moves: {player_moves}", True, (200, 200, 255))
            screen.blit(moves_text, (panel_x + 10, y_offset))
            y_offset += 30
        
        # ספירת כלים של השחקן הנוכחי
        player_pieces = [p for p in game_pieces.values() if hasattr(p, 'color') and p.color == player_color]
        pieces_count = len(player_pieces)
        
        pieces_text = self.font_normal.render(f"🎯 Pieces: {pieces_count}", True, (255, 255, 255))
        screen.blit(pieces_text, (panel_x + 10, y_offset))
        y_offset += 30
        
        # ספירת מלכים של השחקן
        player_kings = [p for p in player_pieces if p.piece_type == "K"]
        kings_count = len(player_kings)
        
        kings_text = self.font_normal.render(f"👑 King: {kings_count}", True, (255, 215, 0))
        screen.blit(kings_text, (panel_x + 10, y_offset))
        y_offset += 30
        
        # זמן משחק
        game_duration = time.time() - start_time
        time_text = self.font_small.render(f"⏱️ Time: {game_duration:.1f}s", True, (200, 200, 200))
        screen.blit(time_text, (panel_x + 10, y_offset))
        y_offset += 25
        
        # מידע על הבחירה הנוכחית של השחקן
        selection_title = self.font_normal.render("🎮 SELECTION:", True, (100, 100, 255))
        screen.blit(selection_title, (panel_x + 10, y_offset))
        y_offset += 25
        
        selected = selection[player]['selected']
        if selected:
            selection_text = self.font_small.render(f"Selected: {selected.piece_id}", True, (255, 255, 255))
            screen.blit(selection_text, (panel_x + 10, y_offset))
            y_offset += 20
        else:
            no_selection_text = self.font_small.render("No piece selected", True, (150, 150, 150))
            screen.blit(no_selection_text, (panel_x + 10, y_offset))
            y_offset += 20
        
        # בקרות בסיסיות לשחקן
        y_offset += 20
        if player == 'A':
            controls_text = self.font_small.render("↑↓←→ + Enter", True, (200, 200, 200))
        else:
            controls_text = self.font_small.render("WASD + Space", True, (200, 200, 200))
        screen.blit(controls_text, (panel_x + 10, y_offset))
