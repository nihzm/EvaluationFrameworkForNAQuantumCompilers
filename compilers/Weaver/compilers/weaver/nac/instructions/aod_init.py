from .base import Instruction
from ..fpqa import FPQA

class AODInit(Instruction):
    def __init__(self, fpqa: FPQA):
        self.fpqa = fpqa

    def apply(self):
        if not self.verify():
            raise ValueError("Cannot apply aod init in current FPQA setting")

    def verify(self) -> bool:
        return True

    def qasm(self) -> str:
        rows = f"[{', '.join(self.fpqa.aod.rows)}]"
        cols = f"[{', '.join(self.fpqa.aod.cols)}]"
        return f"@aod {cols} {rows}"

    def avg_fidelity(self) -> float:
        return 1.0

    def duration() -> float:
        return 0.0