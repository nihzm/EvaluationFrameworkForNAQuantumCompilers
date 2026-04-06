from .atom import Atom

class AOD:
    def __init__(self,  distance: float, rows: int, cols: int):
        self.rows = [distance * row for row in range(rows)]
        self.cols = [distance * col for col in range(cols)]
        self.atom_map = [[None for _ in range(cols)] for _ in range(rows)]

    def set_trap(self, x: int, y: int, atom: Atom | None):
        self.atom_map[y][x] = atom
        if atom is not None:
            atom.assign_trap(False, y, x)

    def get_atom_at_trap(self, x: int, y: int) -> Atom | None:
        return self.atom_map[y][x]

    def occupied(self, x: int, y: int) -> bool:
        return self.atom_map[y][x] != None

    def position(self, x: int, y: int) -> tuple[int]:
        return self.cols[x], self.rows[y]
    