from .base import Instruction
from ..fpqa import FPQA
from ..atom import Atom

class LocalRaman(Instruction):
    def __init__(self, fpqa: FPQA, atom: Atom, x_angle: float, y_angle: float, z_angle: float):
        self.fpqa = fpqa
        self.atom = atom
        self.x_angle = x_angle
        self.y_angle = y_angle
        self.z_angle = z_angle
    
    def apply(self):
        if not self.verify():
            raise ValueError("Cannot apply local Raman pulse in current FPQA setting.")

    def verify(self) -> bool:
        count = 0
        for atom in self.fpqa.atoms:
            if atom == self.atom:
                count += 1
        return count == 1

    def qasm(self) -> str:
        lines = [f"@raman local q[{self.atom.id}] ({self.x_angle}, {self.y_angle}, {self.z_angle})",
                f"U({self.x_angle}, {self.y_angle}, {self.z_angle}) q[{self.atom.id}]\n"]
        return "\n".join(lines)

    def avg_fidelity(self) -> float:
        return self.fpqa.config.U3_GATE_FIDELITY

    def duration(self) -> float:
        return self.fpqa.config.U3_GATE_DURATION

class GlobalRaman(Instruction):
    def __init__(self, fpqa: FPQA, x_angle: float, y_angle: float, z_angle: float):
        self.fpqa = fpqa
        self.x_angle = x_angle
        self.y_angle = y_angle
        self.z_angle = z_angle
    
    def apply(self):
        if not self.verify():
            raise ValueError("Cannot apply global Raman pulse in current FPQA setting.")

    def verify(self) -> bool:
        return True

    def qasm(self) -> str:
        qubit_args = ", ".join([f"q[{atom.id}]" for atom in self.fpqa.atoms])
        lines = [f"@raman global ({self.x_angle}, {self.y_angle}, {self.z_angle})",
                 f"u3_global({self.x_angle}, {self.y_angle}, {self.z_angle}) {qubit_args};\n"]
        return "\n".join(lines)

    def avg_fidelity(self) -> float:
        return self.fpqa.config.U3_GATE_FIDELITY ** len(self.fpqa.atoms)

    def duration(self) -> float:
        return self.fpqa.config.U3_GATE_DURATION