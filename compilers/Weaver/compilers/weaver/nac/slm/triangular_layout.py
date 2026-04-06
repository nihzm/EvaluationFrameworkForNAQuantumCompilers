from math import sqrt
from .base import SLM
from .trap import Trap
from ..atom import Atom

class TriangularLayout(SLM):
    def __init__(self, distance: float, rows: int, cols: int):
        if distance <= 0:
            raise ValueError("Invalid distance.")
        if rows <= 0:
            raise ValueError("Invalid number of rows.")
        if cols <= 0:
            raise ValueError("Invalid number of cols.")
        xy_distance = distance / sqrt(2)
        self.traps = [
            [
                Trap(col * distance + xy_distance if row % 2 == 1 else col * distance, row * xy_distance, None) 
                for col in range(cols)
            ] 
            for row in range(rows)
        ]

    def set_trap(self, x: int, y: int, atom: Atom | None):
        self.traps[y][x].atom = atom
        if atom is not None:
            atom.assign_trap(True, y, x)

    def get_atom_at_trap(self, x: int, y: int) -> Atom | None:
        return self.traps[y][x].atom

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
