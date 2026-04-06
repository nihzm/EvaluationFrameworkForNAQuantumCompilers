from ..nac.fpqa import FPQA
from ..nac.atom import Atom
from pysat.formula import CNF
from ..utils.sat_utils import get_color_map
from math import ceil

class Max3satQaoaMapper:
    def __init__(self, fpqa: FPQA, formula: CNF):
        num_colors, color_map = get_color_map(formula)
        self.fpqa = fpqa
        self.formula = formula
        self.num_colors = num_colors
        self.color_map = color_map
        self.color_groups = [set() for i in range(num_colors)]
        self.max_color_group_size = 0
        self.last_unused_atom = len(fpqa.atoms) - 1
        for clause in range(len(formula.clauses)):
            self.color_groups[color_map[clause]].add(clause)
            self.max_color_group_size = max(self.max_color_group_size, len(self.color_groups[color_map[clause]]))
        if len(fpqa.aod.cols) < self.max_color_group_size:
            raise ValueError("Cannot map formula to FPQA")

    def get_atom_map(self) -> list[Atom]:
        if hasattr(self, "atom_map"):
            return self.atom_map, self.rev_atom_map
        atom_map = [None for _ in range(self.formula.nv)]
        rev_atom_map = {}
        for color in range(len(self.color_groups)):
            for clause in self.color_groups[color]:
                literals = list(map(abs, self.formula.clauses[clause]))
                for literal in literals:
                    if atom_map[literal - 1] is not None:
                        continue
                    atom_map[literal - 1] = self.fpqa.atoms[self.last_unused_atom]
                    rev_atom_map[atom_map[literal - 1].id] = literal
                    self.last_unused_atom -= 1
        self.atom_map = atom_map
        self.rev_atom_map = rev_atom_map
        return atom_map, rev_atom_map

    def get_clause_map(self) -> list[tuple]:
        if hasattr(self, "clause_map"):
            return self.clause_map
        r = 1
        c = ceil(2.0 * self.formula.nv / 3.0) + 1
        traps = self.fpqa.slm.traps
        clause_map = [None for _ in range(len(self.formula.clauses))]
        aod_literals = {}
        for color in range(len(self.color_groups)):
            for clause in self.color_groups[color]:
                literals = list(map(abs, self.formula.clauses[clause]))
                clause_traps = (r, c), (r, c + 1), (r + 1, c + 1)
                aod_pair = (0, 1)
                if (literals[0], literals[2]) in aod_literals or (literals[2], literals[0]) in aod_literals:
                    clause_traps = (r, c), (r + 1, c + 1), (r, c + 1)
                    aod_pair = (0, 2)
                elif (literals[1], literals[2]) in aod_literals or (literals[2], literals[1]) in aod_literals:
                    clause_traps = (r + 1, c + 1), (r, c), (r, c + 1)  
                    aod_pair = (1, 2)
                aod_literals[(literals[aod_pair[0]], literals[aod_pair[1]])] = True
                clause_map[clause] = clause_traps
                c += 3
            r += 2
        self.clause_map = clause_map
        return clause_map

    def get_aod_slm_quadratic_terms(self) -> dict[tuple[int, int], int]:
        if hasattr(self, "aod_slm_quadratic_terms"):
            return self.aod_slm_quadratic_terms
        quadratic_terms = {}
        clause_map = self.get_clause_map()
        for color in range(len(self.color_groups)):
            for clause in self.color_groups[color]:
                literals = list(map(abs, self.formula.clauses[clause]))
                literal_signs = list(map(lambda l: 1 if l > 0 else -1, self.formula.clauses[clause]))
                clause_traps = clause_map[clause]
                for i in range(len(clause_traps)):
                    for j in range(i + 1, len(clause_traps)):
                        (r1, c1), (r2, c2) = clause_traps[i], clause_traps[j]
                        if r1 == r2:
                            continue
                        term = literal_signs[i] * literal_signs[j]
                        l1, l2 = literals[i], literals[j]
                        if l1 > l2:
                            l2, l1 = l1, l2
                        if (l1, l2) not in quadratic_terms:
                            quadratic_terms[(l1, l2)] = 0
                        quadratic_terms[(l1, l2)] += term
        self.aod_slm_quadratic_terms = quadratic_terms
        return quadratic_terms
                        
            
                    
        
                    
                
        
        
        
    