@echo off
echo Starting Kung Fu Chess...
cd /d "%~dp0\.."
set PYTHONPATH=.
python shared\launch_game.py
pause
