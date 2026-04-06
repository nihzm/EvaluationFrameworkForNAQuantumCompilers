from abc import ABC, abstractmethod
from ..fpqa import FPQA

class Instruction(ABC):
    @abstractmethod
    def apply():
        pass

    @abstractmethod
    def verify() -> bool:
        pass

    @abstractmethod
    def qasm() -> str:
        pass

    @abstractmethod
    def avg_fidelity() -> float:
        pass

    @abstractmethod
    def duration() -> float:
        pass

    