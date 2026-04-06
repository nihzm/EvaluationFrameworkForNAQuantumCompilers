from .base import Instruction
from ..fpqa import FPQA

class SLMInit(Instruction):
    def __init__(self, fpqa: FPQA):
        self.fpqa = fpqa

    def apply(self):
        if not self.verify():
            raise ValueError("Cannot apply slm init in current FPQA setting")

    def verify(self) -> bool:
        return True

    def qasm(self) -> str:
        trap_list = self.fpqa.slm.trap_list()
        trap_list = [f"({trap.x}, {trap.y})" for trap in trap_list]
        return f"@slm {trap_list}"

    def avg_fidelity(self) -> float:
        return 1.0

    def duration() -> float:
        return 0.0