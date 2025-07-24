from It1_interfaces.EventTypes import MOVE_DONE, PIECE_CAPTURED
class ScoreManager:
    def __init__(self):
        self.score = {"White": 0, "Black": 0}
    def update(self, event_type, data):
        if event_type == PIECE_CAPTURED:
            piece = data.get("piece")
            color = getattr(piece, "color", None)
            if color:
                self.score[color] += 1
        elif event_type == MOVE_DONE:
            pass
