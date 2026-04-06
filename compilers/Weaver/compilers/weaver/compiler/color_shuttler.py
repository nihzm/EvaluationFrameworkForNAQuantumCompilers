from ..nac.fpqa import FPQA
from ..nac.atom import Atom
from ..nac.instructions.base import Instruction
from ..nac.instructions.shuttle import Shuttle
from ..nac.instructions.parallel import Parallel
from ..nac.instructions.trap_transfer import TrapTransfer
from .color_mapper import Max3satQaoaMapper
from .program import FPQAProgram
from pysat.formula import CNF

class Max3satQaoaShuttler:
    def __init__(self, fpqa: FPQA, mapper: Max3satQaoaMapper, formula: CNF, program: FPQAProgram):
        self.fpqa = fpqa
        self.mapper = mapper
        self.formula = formula
        self.program = program
    
    def shuttle_color(self, color: int):
        atom_map, rev_atom_map = self.mapper.get_atom_map()
        clause_map = self.mapper.get_clause_map()
        color_map = self.mapper.color_map
        clauses = self.mapper.color_groups[color]
        sorted_clauses = list(clauses)
        sorted_clauses.sort(key = lambda clause: self.fpqa.slm.traps[clause_map[clause][0][0]][clause_map[clause][0][1]].x)
        participating_atoms = set()
        for clause in sorted_clauses:
            for literal in self.formula.clauses[clause]:
                participating_atoms.add(atom_map[abs(literal) - 1].id)
        trap_map = {}
        max_slm_row = 0
        for clause in clauses:
            traps = clause_map[clause]
            literals = list(map(abs, self.formula.clauses[clause]))
            for i in range(len(literals)):
                trap_map[literals[i]] = traps[i]
                max_slm_row = max(max_slm_row, traps[i][0])
        last_clause = sorted(clause_map[sorted_clauses[-1]], key = lambda trap: trap[0])
        if last_clause[0][1] > last_clause[1][1]:
            tmp = last_clause[1]
            last_clause[1] = last_clause[0]
            last_clause[0] = last_clause[1]
        last_trap = self.fpqa.slm.traps[last_clause[1][0]][last_clause[1][1]]
        prev_trap = self.fpqa.slm.traps[last_clause[0][0]][last_clause[0][1]]
        prev_y = self.fpqa.aod.rows[0]
        shuttle_map = {}
        num_shuttle = 0
        for clause in clauses:
            literals = list(map(abs, self.formula.clauses[clause]))
            for literal in literals:
                shuttle_map[literal] = False
            num_shuttle += 3
        while num_shuttle > 0:
            last_x = 2 * last_trap.x - prev_trap.x
            trap_switches_up = set()
            trap_switches_down = set()
            instructions = []
            for c in reversed(range(len(self.fpqa.aod.cols))):
                atom = self.fpqa.aod.get_atom_at_trap(c, 0)
                if atom is None or atom.id not in participating_atoms:
                    last_x -= self.fpqa.config.AOD_BEAM_PROXIMITY # 2 * self.fpqa.config.AOD_BEAM_PROXIMITY
                    instruction = Shuttle(self.fpqa, False, c, last_x - self.fpqa.aod.cols[c])
                    instructions.append(instruction)
                else:
                    literal = rev_atom_map[atom.id]
                    trap = self.fpqa.slm.traps[trap_map[literal][0]][trap_map[literal][1]]
                    instruction = Shuttle(self.fpqa, False, c, trap.x - self.fpqa.aod.cols[c])
                    if trap.x > last_x:
                        last_x -= self.fpqa.config.AOD_BEAM_PROXIMITY # 2 * self.fpqa.config.AOD_BEAM_PROXIMITY
                        instruction = Shuttle(self.fpqa, False, c, last_x - self.fpqa.aod.cols[c])
                        instructions.append(instruction)
                        continue
                    instructions.append(instruction)
                    if trap_map[literal][0] != max_slm_row:
                        trap_switches_up.add(((0, c), (trap_map[literal][0], trap_map[literal][1])))
                    else:
                        trap_switches_down.add(((0, c), (trap_map[literal][0], trap_map[literal][1])))
                    num_shuttle -= 1
                    last_x = trap.x
            if len(trap_switches_up) == 0 and len(trap_switches_down) == 0:
                print(last_x, trap.x)
                raise ValueError("Something wrong occurred in shuttler!")
            parallel = Parallel(instructions)
            self.program.add_instruction(parallel)
            if len(trap_switches_up) > 0:
                instruction = Shuttle(self.fpqa, True, 0, last_trap.y - self.fpqa.aod.rows[0])
                self.program.add_instruction(instruction)
                instructions = []
                for (aod_r, aod_c), (slm_r, slm_c) in trap_switches_up:
                    transfer = TrapTransfer(self.fpqa, slm_r, slm_c, aod_r, aod_c)
                    instructions.append(transfer)
                parallel = Parallel(instructions)
                self.program.add_instruction(parallel)
            if len(trap_switches_down) > 0:
                y_pos = self.fpqa.slm.traps[last_clause[2][0]][last_clause[2][1]].y
                instruction = Shuttle(self.fpqa, True, 0, y_pos - self.fpqa.aod.rows[0])
                self.program.add_instruction(instruction)
                instructions = []
                for (aod_r, aod_c), (slm_r, slm_c) in trap_switches_down:
                    transfer = TrapTransfer(self.fpqa, slm_r, slm_c, aod_r, aod_c)
                    instructions.append(transfer)
                parallel = Parallel(instructions)
                self.program.add_instruction(parallel)
            instruction = Shuttle(self.fpqa, True, 0, prev_y - self.fpqa.aod.rows[0])
            self.program.add_instruction(instruction)
        first_clause = sorted(clause_map[sorted_clauses[0]], key = lambda trap: trap[0])
        if first_clause[0][1] > first_clause[1][1]:
            tmp = first_clause[1]
            first_clause[1] = first_clause[0]
            first_clause[0] = tmp
        first_trap = self.fpqa.slm.traps[first_clause[0][0]][first_clause[0][1]]
        instruction = Shuttle(self.fpqa, True, 0, first_trap.y - self.fpqa.aod.rows[0])
        self.program.add_instruction(instruction)
        last_trap_r, last_trap_c = first_clause[0][0], first_clause[0][1]
        last_trap = self.fpqa.slm.traps[last_trap_r][last_trap_c]
        last_x = last_trap.x
        trap_switches = set()
        instructions = []
        for c in reversed(range(len(self.fpqa.aod.cols))):
            atom = self.fpqa.aod.get_atom_at_trap(c, 0)
            if atom is None:
                last_x -= 2 * self.fpqa.config.AOD_BEAM_PROXIMITY
                instruction = Shuttle(self.fpqa, False, c, last_x - self.fpqa.aod.cols[c])
                instructions.append(instruction)
            else:
                last_trap_c -= 2
                last_trap = self.fpqa.slm.traps[last_trap_r][last_trap_c]
                last_x = last_trap.x
                instruction = Shuttle(self.fpqa, False, c, last_x - self.fpqa.aod.cols[c])
                instructions.append(instruction)
                trap_switches.add(((0, c), (last_trap_r, last_trap_c)))
        parallel = Parallel(instructions)
        self.program.add_instruction(parallel)
        instructions = []
        for (aod_r, aod_c), (slm_r, slm_c) in trap_switches:
            transfer = TrapTransfer(self.fpqa, slm_r, slm_c, aod_r, aod_c)
            instructions.append(transfer)
        parallel = Parallel(instructions)
        self.program.add_instruction(parallel)
        atoms = [atom for atom in self.fpqa.atoms]
        atoms.sort(key = lambda atom: self.fpqa.slm.traps[atom.row][atom.col].x)
        instructions = []
        trap_switches = set()
        for c in range(len(self.fpqa.aod.cols)):
            instruction = Shuttle(self.fpqa, False, c, self.fpqa.slm.traps[atoms[c].row][atoms[c].col].x - self.fpqa.aod.cols[c])
            instructions.append(instruction)
            if abs(self.fpqa.slm.traps[atoms[c].row][atoms[c].col].y - self.fpqa.aod.rows[0]) < 1e-09:
                trap_switches.add(((0, c), (atoms[c].row, atoms[c].col)))
        parallel = Parallel(instructions)
        self.program.add_instruction(parallel)
        instructions = []
        for (aod_r, aod_c), (slm_r, slm_c) in trap_switches:
            transfer = TrapTransfer(self.fpqa, slm_r, slm_c, aod_r, aod_c)
            instructions.append(transfer)    
        parallel = Parallel(instructions)
        self.program.add_instruction(parallel)
                
            
            
            
        
                    
