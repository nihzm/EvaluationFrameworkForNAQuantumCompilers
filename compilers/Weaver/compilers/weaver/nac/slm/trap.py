from ..atom import Atom

class Trap:
    def __init__(self, x: float, y: float, atom: Atom | None):
        self.x = x
        self.y = y
        self.atom = atom