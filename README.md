# 🥋 Kung Fu Chess - Real-Time Chess Game

**Kung Fu Chess** is a real-time, two-player chess-inspired game where both players can move simultaneously — no turns, just action!

This project was built using Python and OpenCV, with a focus on timing, input handling, and visual feedback for game states.

## 🎮 Features

- 🕒 Real-Time Gameplay — no turns, players act simultaneously  
- 👥 Two-Player Control System:  
  - Player A: Arrow Keys + Enter  
  - Player B: WASD + Spacebar  
- 🧠 Piece States:
  - Idle → Jump (1s cooldown) or Move (2s cooldown)
- ✅ Move Validation — only legal moves are allowed
- 🎨 Visual Feedback:
  - Colored selection frames (Red / Blue)
  - Frozen overlay when piece is in cooldown
- 🧩 Modular Design:
  - Separate classes for pieces, board, input commands, and image handling

## 📁 Project Structure

```
project/
│
├── Game.py          # Main game logic and loop
├── Board.py         # Handles board grid and image rendering
├── Piece.py         # Represents each chess piece and its behavior
├── Command.py       # Encapsulates player actions
├── img.py           # Image utilities (loading, drawing overlays, etc.)
├── assets/          # Folder for board/piece images and overlays
├── run_game.bat     # (Optional) Batch file to run the game on Windows
└── README.md        # This file
```

## 🕹️ Controls

| Player   | Movement Keys | Action Key |
|----------|----------------|------------|
| Player A | Arrow Keys     | Enter      |
| Player B | W A S D        | Spacebar   |

## 🔄 Game Rules

- Each player moves a **selection cursor** across the board
- Press the action key **on your piece** → Jump (1s cooldown)
- Press the action key **on a valid target square** → Move (2s cooldown)
- While on cooldown, the piece is shown with a visual overlay (gray or yellow)
- Win conditions (e.g., king capture) to be added in future versions

## 🚀 How to Run

1. Make sure you have Python 3.8+ and `opencv-python` installed:

```bash
pip install opencv-python
```

2. Place your board and piece images inside the `assets/` folder.

3. Run the game:

```bash
python Game.py
```

Or on Windows:

```bash
run_game.bat
```

## 🛠️ Developer Notes

- Add or customize piece types in `Piece.py`
- Implement capture logic in the `_resolve_collisions()` method
- Legal moves per piece are handled in `_is_valid_move()`

## 👩‍💻 Built By

**Tamar**  
Final project for **Kamatech Bootcamp 2025**
