from pysat.formula import CNF
from .program import FPQAProgram
from .color_mapper import Max3satQaoaMapper
from .color_shuttler import Max3satQaoaShuttler
from .color_executor import Max3satQaoaExecutor
from ..utils.sat_utils import get_color_map
from ..nac.fpqa import FPQA
from ..nac.config import FPQAConfig
from ..nac.aod import AOD
from ..nac.slm.triangular_layout import TriangularLayout
from ..nac.config import FPQAConfig
from ..nac.atom import Atom
from ..nac.instructions.raman import GlobalRaman
import numpy as np


class Max3satQaoaCompiler:
    def __init__(self, formula: CNF, config: None | FPQAConfig = None):
        self.formula = formula
        self.config = config

    def _qaoa_equal_superposition(self, program: FPQAProgram):
        program.add_instruction(GlobalRaman(program.fpqa, np.pi / 2.0, 0.0, np.pi))

    def _qaoa_mixer(self, program: FPQAProgram, parameter: float):
        program.add_instruction(GlobalRaman(program.fpqa, parameter, 0.0, 0.0))

    def compile_single_layer(self) -> FPQAProgram:
        num_colors, color_map = get_color_map(self.formula)
        num_slm_rows = (num_colors + 1) * 2
        num_slm_cols = len(self.formula.clauses) * 3 + self.formula.nv * 2
        num_aod_rows = 1
        num_aod_cols = self.formula.nv
        config = self.config
        aod = AOD(config.INTERACTION_RADIUS / 2.0, num_aod_rows, num_aod_cols)
        slm = TriangularLayout(config.INTERACTION_RADIUS, num_slm_rows, num_slm_cols)
        atoms = [Atom(i + 1, False, 0, i) for i in range(self.formula.nv)]
        fpqa = FPQA(slm, aod, atoms, config)
        program = FPQAProgram(fpqa)
        mapper = Max3satQaoaMapper(fpqa, self.formula)
        shuttler = Max3satQaoaShuttler(fpqa, mapper, self.formula, program)
        executor = Max3satQaoaExecutor(fpqa, mapper, self.formula, program)
        self._qaoa_equal_superposition(program)
        # TO-DO: Randomize parameter
        parameter = 0.2512 * np.pi
        for color in range(num_colors):

            shuttler.shuttle_color(color)
            executor.execute_color(color, parameter)
        executor.implement_linear_terms(parameter)
        # TO-DO: Randomize parameter
        parameter = 0.1235 * np.pi
        self._qaoa_mixer(program, parameter)
        for atom_pair in executor.quadratic_terms:
            if abs(executor.quadratic_terms[atom_pair]) > 1:
                print(atom_pair, executor.quadratic_terms[atom_pair])
        return program