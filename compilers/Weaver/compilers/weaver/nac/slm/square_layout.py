from nac.slm.base import SLM
from nac.slm.trap import Trap
from nac.atom import Atom

class SquareGrid(SLM):
    def __init__(self, distance: float, rows: int, cols: int):
        if distance <= 0:
            raise ValueError("Invalid distance.")
        if rows <= 0:
            raise ValueError("Invalid number of rows.")
        if cols <= 0:
            raise ValueError("Invalid number of cols.")
        self.traps = [
            [
                Trap(distance * col, distance * row, None) 
                for col in range(cols)
            ]
            for row in range(rows)
        ]

    def set_trap(self, x: int, y: int, atom: Atom | None):
        self.traps[y][x].atom = atom

    def get_atom_at_trap(self, x: int, y: int) -> Atom | None:
        return self.traps[y][x]

    def occupied(self, x: int, y: int) -> bool:
        return self.traps[y][x].atom != None

    def position(self, x: int, y: int) -> tuple[int]:
        return self.traps[y][x].x, self.traps[y][x].y

    def trap_list(self) -> list[Trap]:
        return [
            trap 
            for trap in column 
            for column in self.traps
        ]
        