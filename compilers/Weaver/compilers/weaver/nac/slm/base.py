from abc import ABC, abstractmethod
from ..atom import Atom
from ..slm.trap import Trap

class SLM(ABC):
    @abstractmethod
    def set_trap(self, x: int, y: int, atom: Atom | None):
        pass

    @abstractmethod
    def get_atom_at_trap(self, x: int, y: int) -> Atom | None:
        pass

    @abstractmethod
    def occupied(self, x: int, y: int) -> bool:
        pass

    @abstractmethod
    def position(self, x: int, y: int) -> tuple[int]:
        pass

    @abstractmethod
    def trap_list(self) -> list[Trap]:
        pass