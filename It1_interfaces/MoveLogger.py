from It1_interfaces.EventTypes import MOVE_DONE
import time

class MoveLogger:
    def __init__(self):
        self.move_history = []
        self.game_start_time = time.time()
    
    def update(self, event_type, data):
        if event_type == MOVE_DONE:
            command = data.get("command")
            if command:
                timestamp = time.time() - self.game_start_time
                move_entry = {
                    "time": round(timestamp, 2),
                    "piece_id": command.piece_id,
                    "command_type": command.type,
                    "params": command.params if hasattr(command, 'params') else []
                }
                self.move_history.append(move_entry)
                
                # Determine piece color and type from piece_id
                piece_color = "White" if "W" in command.piece_id else "Black"
                piece_type = command.piece_id[0] if command.piece_id else "?"
    
    def get_move_history(self):
        """Get complete move history."""
        return self.move_history.copy()
    
    def get_recent_moves(self, count=5):
        """Get the last N moves."""
        return self.move_history[-count:] if self.move_history else []
    
    def display_move_summary(self):
        """Display move statistics."""
        if not self.move_history:
            return
            
        white_moves = len([m for m in self.move_history if "W" in m["piece_id"]])
        black_moves = len([m for m in self.move_history if "B" in m["piece_id"]])
        
        print("=" * 50)
        print("📝 MOVE SUMMARY 📝")
        print(f"Total moves: {len(self.move_history)}")
        print(f"White moves: {white_moves}")
        print(f"Black moves: {black_moves}")
        print(f"Game duration: {self.move_history[-1]['time']:.1f}s" if self.move_history else "0s")
        print("=" * 50)
