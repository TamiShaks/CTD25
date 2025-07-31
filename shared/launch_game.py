#!/usr/bin/env python3
"""
Chess Game Launcher
Unified entry point for client-server chess game
"""

import sys
import os
from pathlib import Path

def setup_paths():
    """Add all necessary paths to sys.path"""
    base_path = Path(__file__).parent.parent.absolute()
    
    # Add client, server, and shared paths
    paths_to_add = [
        base_path / "shared" / "interfaces",
        base_path / "client" / "interfaces",
        base_path / "server" / "interfaces",
        base_path / "shared",
        base_path / "client",
        base_path / "server",
        base_path
    ]
    
    for path in paths_to_add:
        if path.exists():
            sys.path.insert(0, str(path))
    
    # Change working directory to base for relative paths
    os.chdir(str(base_path))

def main():
    """Main entry point for the chess game"""
    setup_paths()
    
    # Import and run the main game from client
    from client.main import main as client_main
    client_main()

if __name__ == "__main__":
    main()
