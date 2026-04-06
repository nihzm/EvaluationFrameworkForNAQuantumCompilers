from .base import Instruction
from ..fpqa import FPQA
from ..atom import Atom

class Bind(Instruction):
    def __init__(self, fpqa: FPQA, qid: str, atom: Atom, is_slm: bool, row: int, col: int):
        self.fpqa = fpqa
        self.qid = qid
        self.atom = atom
        self.is_slm = is_slm
        self.row = row
        self.col = col

    def apply(self):
        if not self.verify():
            raise ValueError("Cannot apply bind in current FPQA setting")
        if self.is_slm:
            self.fpqa.slm.set_trap(self.col, self.row, self.atom)
        else:
            self.fpqa.aod.set_trap(self.col, self.row, self.atom)

    def verify(self) -> bool:
        if atom.is_slm and self.fpqa.slm.get_atom_at_trap(self.col, self.row) is not None:
            return False
        if not atom.is_slm and self.aod.get_atom_at_trap(self.col, self.row) is not None:
            return False
        if self.is_slm:
            return self._verify_slm()
        return self._verify_aod()

    def _verify_aod(self) -> bool:
        return (self.row >= 0 and self.row < len(self.fpqa.aod.rows) and 
            self.col >= 0 and self.col < len(self.fpqa.aod.cols))

    def _verify_slm(self) -> bool:
        return self.row >= 0 and self.row < len(self.fpqa.slm.traps) and self.col >= 0 and self.col < len(self.fpqa.slm.traps[self.row]) 

    def qasm(self) -> str:
        trap_type = "slm" if self.is_slm else "aod"
        index =  self.col * len(self.slm.traps) + self.row if self.is_slm else f"({self.col}, {self.row})"
        return f"@bind {self.qid} {trap_type} {index}"

    def avg_fidelity(self) -> float:
        return 1.0

    def duration(self) -> float:
        return 0.0