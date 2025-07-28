#!/usr/bin/env python3
"""
🧪 Test Promotion UI
===================

Quick test to see how the promotion popup looks.
"""

import pygame
import sys
from It1_interfaces.PromotionUI import PromotionUI

def test_promotion_ui():
    """Test the promotion UI display."""
    pygame.init()
    
    # Create a test window
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("🎮 Pawn Promotion Test")
    
    # Create promotion UI
    promotion_ui = PromotionUI(screen_width, screen_height)
    
    # Test state
    selected_option = 0
    options = ["Q", "R", "B", "N"]
    player = "A"
    clock = pygame.time.Clock()
    
    print("🎮 Promotion UI Test - Use Arrow Keys to navigate, ESC to exit")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_LEFT and selected_option > 0:
                    selected_option -= 1
                elif event.key == pygame.K_RIGHT and selected_option < len(options) - 1:
                    selected_option += 1
                elif event.key == pygame.K_SPACE:
                    player = "B" if player == "A" else "A"
                    print(f"Switched to Player {player}")
        
        # Clear screen with a chess board pattern
        screen.fill((240, 217, 181))
        
        # Draw some fake chess board squares
        for row in range(8):
            for col in range(8):
                color = (181, 136, 99) if (row + col) % 2 == 1 else (240, 217, 181)
                square_size = 60
                x = col * square_size + 50
                y = row * square_size + 50
                pygame.draw.rect(screen, color, (x, y, square_size, square_size))
        
        # Draw promotion popup
        promotion_ui.draw_promotion_popup(screen, player, selected_option, options)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("✅ Promotion UI test completed!")

if __name__ == "__main__":
    test_promotion_ui()
