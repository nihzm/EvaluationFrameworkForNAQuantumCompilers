from .program import FPQAProgram
from .color_mapper import Max3satQaoaMapper
from pysat.formula import CNF
from ..nac.fpqa import FPQA
from ..nac.atom import Atom
from ..utils.hamiltonians import Max3satHamiltonian
from ..nac.instructions.raman import GlobalRaman, LocalRaman
from ..nac.instructions.rydberg import Rydberg
from ..nac.instructions.shuttle import Shuttle
from ..nac.instructions.parallel import Parallel
from ..nac.instructions.trap_transfer import TrapTransfer
import numpy as np

class Max3satQaoaExecutor:
    def __init__(self, fpqa: FPQA, mapper: Max3satQaoaMapper, formula: CNF,  program: FPQAProgram):
        self.fpqa = fpqa
        self.formula = formula
        self.mapper = mapper
        self.program = program
        self.hamiltonian = Max3satHamiltonian(formula=formula)
        # TO-DO: Optimize fidelity in single/quadratic terms
        self.quadratic_terms = {}
        self.linear_terms = {atom.id: 0.0 for atom in fpqa.atoms}

    def _get_slm_qubit_errors(self, aod_pairs: list[tuple[Atom, Atom]], slm_atoms: list[Atom], clauses: list[list[int]]) -> list[float]:
        atom_map, rev_atom_map = self.mapper.get_atom_map()
        slm_qubit_errors = [0.0 for _ in clauses]
        for i, clause in enumerate(clauses):
            literal_sign = {abs(l): 1 if l > 0 else -1 for l in self.formula.clauses[clause]}
            pos_count = sum(map(lambda l: 1 if l > 0 else 0, self.formula.clauses[clause]))
            if pos_count == 3:
                slm_qubit_errors[i] = 1.0
            elif pos_count == 2 and literal_sign[rev_atom_map[slm_atoms[i].id]] == -1:
                slm_qubit_errors[i] = -1.0
            elif pos_count == 2 and literal_sign[rev_atom_map[aod_pairs[i][0].id]] == -1:
                slm_qubit_errors[i] = 1.0
            elif pos_count == 2 and literal_sign[rev_atom_map[aod_pairs[i][1].id]] == -1:
                slm_qubit_errors[i] = 1.0
            elif pos_count == 1 and literal_sign[rev_atom_map[slm_atoms[i].id]] == 1:
                slm_qubit_errors[i] = 1.0
            elif pos_count == 1 and literal_sign[rev_atom_map[aod_pairs[i][0].id]] == 1:
                slm_qubit_errors[i] = -1.0
            elif pos_count == 1 and literal_sign[rev_atom_map[aod_pairs[i][1].id]] == 1:
                slm_qubit_errors[i] = -1.0
            else:
                slm_qubit_errors[i] = -1.0
        return slm_qubit_errors
    
    def _get_ccnot_angle_signs(self, aod_pairs: list[tuple[Atom, Atom]], slm_atoms: list[Atom], clauses: list[list[int]]) -> list[float]:
        atom_map, rev_atom_map = self.mapper.get_atom_map()
        angle_signs = [1.0 for _ in clauses]
        for i, clause in enumerate(clauses):
            literal_sign = {abs(l): 1 if l > 0 else -1 for l in self.formula.clauses[clause]}
            pos_count = sum(map(lambda l: 1 if l > 0 else 0, self.formula.clauses[clause]))
            if pos_count == 3:
                angle_signs[i] = -1.0
            elif pos_count == 2 and literal_sign[rev_atom_map[slm_atoms[i].id]] == -1:
                pass
            elif pos_count == 2 and literal_sign[rev_atom_map[aod_pairs[i][0].id]] == -1:
                angle_signs[i] = -1.0
            elif pos_count == 2 and literal_sign[rev_atom_map[aod_pairs[i][1].id]] == -1:
                angle_signs[i] = -1.0
            elif pos_count == 1 and literal_sign[rev_atom_map[slm_atoms[i].id]] == 1:
                angle_signs[i] = -1.0
            elif pos_count == 1 and literal_sign[rev_atom_map[aod_pairs[i][0].id]] == 1:
                pass
            elif pos_count == 1 and literal_sign[rev_atom_map[aod_pairs[i][1].id]] == 1:
                pass
            else:
                pass
        return angle_signs

    def _avoid_implemented_quadratic_terms(self, aod_pairs: list[tuple[Atom, Atom]], clauses: list[list[int]]):
        instructions = []
        aod_slm_quadratic_terms = self.mapper.get_aod_slm_quadratic_terms()
        atom_map, rev_atom_map = self.mapper.get_atom_map()
        for i, clause in enumerate(clauses):
            l1, l2 = rev_atom_map[aod_pairs[i][0].id], rev_atom_map[aod_pairs[i][1].id]
            if l1 > l2:
                l2, l1 = l1, l2
            term = 0
            if (l1 - 1, l2 - 1) in self.hamiltonian.quadratic_map:
                term = self.hamiltonian.quadratic_map[(l1 - 1, l2 - 1)]
            if (l1, l2) in aod_slm_quadratic_terms:
                term -= aod_slm_quadratic_terms[(l1, l2)]
            if (l1, l2) not in self.quadratic_terms and term != 0:
                continue
            a1, a2 = aod_pairs[i][0], aod_pairs[i][1]
            if a1.col > a2.col:
                a2, a1 = a1, a2
            offset = self.fpqa.config.INTERACTION_RADIUS / 4.0
            instructions.append(Shuttle(self.fpqa, False, a1.col, -offset))
            instructions.append(Shuttle(self.fpqa, False, a2.col, offset))
        parallel = Parallel(instructions)
        self.program.add_instruction(parallel)

    def _implement_quadratic_terms(self, aod_pairs: list[tuple[Atom, Atom]], slm_atoms: list[Atom], clauses: list[list[int]], parameter: float):
        atom_map, rev_atom_map = self.mapper.get_atom_map()
        aod_slm_quadratic_terms = self.mapper.get_aod_slm_quadratic_terms()
        pairs = []
        for i, clause in enumerate(clauses):
            l1, l2 = rev_atom_map[aod_pairs[i][0].id], rev_atom_map[aod_pairs[i][1].id]
            a1, a2 = aod_pairs[i][0], aod_pairs[i][1]
            if l1 > l2:
                l2, l1 = l1, l2
            if (l1, l2) in self.quadratic_terms:
                continue
            angle = 0
            if (l1 - 1, l2 - 1) in self.hamiltonian.quadratic_map:
                angle = self.hamiltonian.quadratic_map[(l1 - 1, l2 - 1)]
            if (l1, l2) in aod_slm_quadratic_terms:
                angle -= aod_slm_quadratic_terms[(l1, l2)]
            if angle == 0:
                continue
            angle = angle * 2.0 * parameter
            pairs.append((a1, a2, angle))
            self.quadratic_terms[(l1, l2)] = True
        if len(pairs) == 0:
            return
        for a1, a2, angle in pairs:
            self.program.add_instruction(LocalRaman(self.fpqa, a2, np.pi / 2.0, 0.0, np.pi))
        self.program.add_instruction(Rydberg(self.fpqa))
        for a1, a2, angle in pairs:
            self.program.add_instruction(LocalRaman(self.fpqa, a2, angle, 0.0, 0.0))
        self.program.add_instruction(Rydberg(self.fpqa))
        for a1, a2, angle in pairs:
            self.program.add_instruction(LocalRaman(self.fpqa, a2, np.pi / 2.0, 0.0, np.pi))
    
    def _implement_ccnot_control(self, aod_pairs: list[tuple[Atom, Atom]], slm_atoms: list[Atom], clauses: list[list[int]]):
        atom_map, rev_atom_map = self.mapper.get_atom_map()
        for i, clause in enumerate(clauses):
            literal_sign = {abs(l): 1 if l > 0 else -1 for l in self.formula.clauses[clause]}
            pos_count = sum(map(lambda l: 1 if l > 0 else 0, self.formula.clauses[clause]))
            if pos_count == 3:
                pass
            elif pos_count == 2 and literal_sign[rev_atom_map[slm_atoms[i].id]] == -1:
                pass
            elif pos_count == 2 and literal_sign[rev_atom_map[aod_pairs[i][0].id]] == -1:
                self.program.add_instruction(LocalRaman(self.fpqa, aod_pairs[i][0], np.pi, 0.0, 0.0))
            elif pos_count == 2 and literal_sign[rev_atom_map[aod_pairs[i][1].id]] == -1:
                self.program.add_instruction(LocalRaman(self.fpqa, aod_pairs[i][1], np.pi, 0.0, 0.0))
            elif pos_count == 1 and literal_sign[rev_atom_map[slm_atoms[i].id]] == 1:
                self.program.add_instruction(LocalRaman(self.fpqa, aod_pairs[i][0], np.pi, 0.0, 0.0))
                self.program.add_instruction(LocalRaman(self.fpqa, aod_pairs[i][1], np.pi, 0.0, 0.0))
            elif pos_count == 1 and literal_sign[rev_atom_map[aod_pairs[i][0].id]] == 1:
                self.program.add_instruction(LocalRaman(self.fpqa, aod_pairs[i][1], np.pi, 0.0, 0.0))
            elif pos_count == 1 and literal_sign[rev_atom_map[aod_pairs[i][1].id]] == 1:
                self.program.add_instruction(LocalRaman(self.fpqa, aod_pairs[i][0], np.pi, 0.0, 0.0))
            else:
                self.program.add_instruction(LocalRaman(self.fpqa, aod_pairs[i][0], np.pi, 0.0, 0.0))
                self.program.add_instruction(LocalRaman(self.fpqa, aod_pairs[i][1], np.pi, 0.0, 0.0))

    def _add_linear_terms(self, aod_pairs: list[tuple[Atom, Atom]], slm_atoms: list[Atom], clauses: list[list[int]]):
        atom_map, rev_atom_map = self.mapper.get_atom_map()
        slm_qubit_errors = self._get_slm_qubit_errors(aod_pairs, slm_atoms, clauses)
        for i, clause in enumerate(clauses):
            literal_sign = {abs(l): 1 if l > 0 else -1 for l in self.formula.clauses[clause]}
            slm_term = -literal_sign[rev_atom_map[slm_atoms[i].id]]
            if slm_term != slm_qubit_errors[i]:
                self.linear_terms[slm_atoms[i].id] += slm_term - slm_qubit_errors[i]
            self.linear_terms[aod_pairs[i][0].id] += -literal_sign[rev_atom_map[aod_pairs[i][0].id]]
            self.linear_terms[aod_pairs[i][1].id] += -literal_sign[rev_atom_map[aod_pairs[i][1].id]]

    def implement_linear_terms(self, parameter: float):
        for atom in self.fpqa.atoms:
            self.program.add_instruction(LocalRaman(self.fpqa, atom, 0.0, 0.0, 2.0 * self.linear_terms[atom.id] * parameter))            
    
    def execute_color(self, color: int, parameter: float):
        atom_map, rev_atom_map = self.mapper.get_atom_map()
        color_groups = self.mapper.color_groups
        clauses = color_groups[color]
        slm_atoms = []
        aod_atoms = []
        for clause in clauses:
            literals = list(map(abs, self.formula.clauses[clause]))
            aod_pair = []
            for literal in literals:
                if atom_map[literal - 1].is_slm:
                    slm_atoms.append(atom_map[literal - 1])
                else:
                    aod_pair.append(atom_map[literal - 1])
            aod_atoms.append(tuple(aod_pair))
        ccnot_angle_signs = self._get_ccnot_angle_signs(aod_atoms, slm_atoms, clauses)
        self._implement_ccnot_control(aod_atoms, slm_atoms, clauses)
        for atom in slm_atoms:
            self.program.add_instruction(LocalRaman(self.fpqa, atom, np.pi / 2.0, 0.0, np.pi))
        self.program.add_instruction(Rydberg(self.fpqa))
        for i, atom in enumerate(slm_atoms):
            self.program.add_instruction(LocalRaman(self.fpqa, atom, ccnot_angle_signs[i] * 4.0 * parameter, 0.0, 0.0))
        self.program.add_instruction(Rydberg(self.fpqa))
        for atom in slm_atoms:
            self.program.add_instruction(LocalRaman(self.fpqa, atom, np.pi / 2.0, 0.0, np.pi))
        self._implement_ccnot_control(aod_atoms, slm_atoms, clauses)
        self.program.add_instruction(Shuttle(self.fpqa, True, 0, -self.fpqa.config.RESTRICTION_RADIUS))
        self._avoid_implemented_quadratic_terms(aod_atoms, clauses)
        self._implement_quadratic_terms(aod_atoms, slm_atoms, clauses, parameter)
        self._add_linear_terms(aod_atoms, slm_atoms, clauses)
        offset = self.fpqa.slm.traps[slm_atoms[0].row][slm_atoms[0].col].y - self.fpqa.aod.rows[0]
        self.program.add_instruction(Shuttle(self.fpqa, True, 0, offset))
        instructions = []
        slm_atoms.sort(key=lambda atom: atom.col)
        aod_col = len(self.fpqa.aod.cols) - 2
        for atom in reversed(slm_atoms):
            instructions.append(TrapTransfer(self.fpqa, atom.row, atom.col, 0, aod_col))
            aod_col -= 3
        parallel = Parallel(instructions)
        self.program.add_instruction(parallel)
            
            