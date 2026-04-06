from .base import Instruction
from ..fpqa import FPQA

class Shuttle(Instruction):
    def __init__(self, fpqa: FPQA, is_row: bool, index: int, offset: float):
        self.fpqa = fpqa
        self.is_row = is_row
        self.index = index
        self.offset = offset
    
    def apply(self):
        #if not self.verify():
        #    raise ValueError("Cannot apply shuttle in current FPQA setting")
        if self.is_row:
            self.fpqa.aod.rows[self.index] += self.offset
        else:
            self.fpqa.aod.cols[self.index] += self.offset
    
    def verify(self) -> bool:
        if self.is_row:
            return self._verify_row()
        return self._verify_column()

    def _verify_row(self) -> bool:
        next_pos = self.fpqa.aod.rows[self.index] + self.offset
        if self.index > 0:
            if self.fpqa.aod.rows[self.index - 1] > next_pos:
                return False
            if abs(self.fpqa.aod.rows[self.index - 1] - next_pos) < self.fpqa.config.AOD_BEAM_PROXIMITY:
                return False
        if self.index < len(self.fpqa.aod.rows) - 1:
            if self.fpqa.aod.rows[self.index + 1] < next_pos:
                return False
            if abs(self.fpqa.aod.rows[self.index + 1] - next_pos) < self.fpqa.config.AOD_BEAM_PROXIMITY:
                return False
        return True

    def _verify_column(self) -> bool:
        next_pos = self.fpqa.aod.cols[self.index] + self.offset
        if self.index > 0:
            if self.fpqa.aod.cols[self.index - 1] > next_pos:
                return False
            if abs(self.fpqa.aod.cols[self.index - 1] - next_pos) < self.fpqa.config.AOD_BEAM_PROXIMITY:
                return False
        if self.index < len(self.fpqa.aod.cols) - 1:
            if self.fpqa.aod.cols[self.index + 1] < next_pos:
                return False
            if abs(self.fpqa.aod.cols[self.index + 1] - next_pos) < self.fpqa.config.AOD_BEAM_PROXIMITY:
                return False
        return True

    def qasm(self) -> str:
        array_type = "row" if self.is_row else "col"
        return f"@shuttle {array_type} {self.index} {self.offset}\n"

    def avg_fidelity(self) -> float:
        return self.fpqa.config.SHUTTLING_FIDELITY

    def duration(self) -> float:
        return self.offset / self.fpqa.config.SHUTTLING_SPEED