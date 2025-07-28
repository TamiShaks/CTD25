"""
🧪 Comprehensive Test Suite for Kung Fu Chess
==================================================

This package contains unit tests for all components of the chess game system.
All tests are written in English and follow modern testing best practices.

Test Structure:
- test_*.py: Individual unit tests for each class
- test_integration.py: Integration tests for the entire system
- test_runner.py: Main test runner with detailed reporting

Coverage Areas:
✅ Core Classes: Board, Piece, Moves, State, Physics, Graphics
✅ Game Logic: Game, Command, EventBus, ChessRulesValidator
✅ Managers: ScoreManager, SoundManager, AnimationManager, MoveLogger
✅ Input/Output: InputManager, ThreadedInputManager, Img (with mocks)
✅ Factories: PieceFactory, GraphicsFactory, PhysicsFactory
✅ Integration: Full game flow testing

Author: AI Assistant
Date: July 2025
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"

# Test configuration
TEST_CONFIG = {
    "enable_logging": True,
    "verbose_output": True,
    "mock_external_resources": True,
    "test_timeout": 30,  # seconds
}

# Import order for test discovery
__all__ = [
    "test_img_simple",
    "test_command_simple", 
    "test_moves",
    "test_integration",
    "test_coverage_summary",
    "test_board",
    "test_piece", 
    "test_state",
    "test_physics",
    "test_graphics",
    "test_runner"
]
