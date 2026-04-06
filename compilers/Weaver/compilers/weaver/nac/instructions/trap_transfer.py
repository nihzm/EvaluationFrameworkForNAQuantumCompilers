from .base import Instruction
from ..fpqa import FPQA

class TrapTransfer(Instruction):
    def __init__(self, fpqa: FPQA, slm_row: int, slm_col: int, aod_row: int, aod_col: int):
        self.fpqa = fpqa
        self.slm_row = slm_row
        self.slm_col = slm_col
        self.aod_row = aod_row
        self.aod_col = aod_col
    
    def apply(self):
        if not self.verify():
            raise ValueError("Cannot apply trap transfer in current FPQA setting.")
        slm_atom = self.fpqa.slm.get_atom_at_trap(self.slm_col, self.slm_row)
        aod_atom = self.fpqa.aod.get_atom_at_trap(self.aod_col, self.aod_row)
        self.fpqa.slm.set_trap(self.slm_col, self.slm_row, aod_atom)
        self.fpqa.aod.set_trap(self.aod_col, self.aod_row, slm_atom)

    def verify(self) -> bool:
        if self.fpqa.slm.occupied(self.slm_col, self.slm_row) and self.fpqa.aod.occupied(self.aod_col, self.aod_row):
            return False
        if not self.fpqa.slm.occupied(self.slm_col, self.slm_row) and not self.fpqa.aod.occupied(self.aod_col, self.aod_row):
            return False
        slm_pos_x, slm_pos_y = self.fpqa.slm.position(self.slm_col, self.slm_row)
        aod_pos_x, aod_pos_y = self.fpqa.aod.position(self.aod_col, self.aod_row)
        dx, dy = slm_pos_x - aod_pos_x, slm_pos_y - aod_pos_y
        distance = dx * dx + dy * dy
        if distance > self.fpqa.config.TRAP_TRANSFER_PROXIMITY:
            return False
        return True

    def qasm(self) -> str:
        slm_index = self.slm_col * len(self.fpqa.slm.traps) + self.slm_row
        return f"@transfer {slm_index} ({self.aod_col}, {self.aod_row})\n"

    def avg_fidelity(self) -> float:
        return self.fpqa.config.TRAP_SWAP_FIDELITY

    def duration(self) -> float:
        return self.fpqa.config.TRAP_SWAP_DURATION