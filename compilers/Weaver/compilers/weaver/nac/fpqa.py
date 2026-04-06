from math import pow, sqrt
from ..nac.atom import Atom
from ..nac.slm.base import SLM
from ..nac.aod import AOD
from ..nac.config import FPQAConfig

class FPQA:
    def __init__(self,  slm: SLM, aod: AOD, atoms: list[Atom], config: FPQAConfig):
        self.aod = aod
        self.slm = slm
        self.atoms = atoms
        for atom in self.atoms:
            if atom.is_slm:
                if self.slm.occupied(atom.col, atom.row):
                    raise ValueError("SLM Trap already occupied.")
                self.slm.set_trap(atom.col, atom.row, atom)
            else:
                if self.aod.occupied(atom.col, atom.row):
                    raise ValueError("AOD Trap already occupied.")
                self.aod.set_trap(atom.col, atom.row, atom)
        self.config = config

    def get_atom(self, index: int) -> Atom:
        return self.atoms[index]

    def is_interacting(self, atom1: Atom, atom2: Atom) -> bool:
        pos1 = 0.0, 0.0
        if atom1.is_slm:
            pos1 = self.slm.position(atom1.col, atom1.row)
        else:
            pos1 = self.aod.position(atom1.col, atom1.row)
        pos2 = 0.0, 0.0
        if atom2.is_slm:
            pos2 = self.slm.position(atom2.col, atom2.row)
        else:
            pos2 = self.aod.position(atom2.col, atom2.row)
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        distance = sqrt(dx * dx + dy * dy)
        return distance <= self.config.INTERACTION_RADIUS
        
            