from .base import Instruction


class Parallel(Instruction):
    def __init__(self, instructions: list[Instruction]):
        self.instructions = instructions
    
    def apply(self):
        for instruction in self.instructions:
            #if not instruction.verify():
            #    raise ValueError("Cannot apply parallel in current FPQA setting")
            instruction.apply()

    def verify(self) -> bool:
        # TO-DO: add proper parallel instruction verification
        return all(instruction.verify() for instruction in self.instructions)

    def qasm(self) -> str:
        instruction_strs = ["@parallel begin\n", *[instruction.qasm() for instruction in self.instructions], "@parallel end\n"]
        return "".join(instruction_strs)

    def avg_fidelity(self) -> float:
        fidelity = 1.0
        for instruction in self.instructions:
            fidelity *= instruction.avg_fidelity()
        return fidelity
    
    def duration(self) -> float:
        duration = 0.0
        for instruction in self.instructions:
            duration = max(duration, instruction.duration())
        return duration