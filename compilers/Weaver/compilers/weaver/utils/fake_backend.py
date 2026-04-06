from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.exceptions import QiskitError
from qiskit.transpiler import CouplingMap, Target, QubitProperties
from qiskit.pulse.instruction_schedule_map import InstructionScheduleMap
from qiskit.circuit.controlflow import IfElseOp, WhileLoopOp, ForLoopOp, SwitchCaseOp, BreakLoopOp, ContinueLoopOp
from math import ceil, floor

_NOISE_DEFAULTS = {
    "cx": (7.992e-08, 8.99988e-07, 1e-5, 5e-3),
    "ecr": (7.992e-08, 8.99988e-07, 1e-5, 5e-3),
    "cz": (7.992e-08, 8.99988e-07, 1e-5, 5e-3),
    "id": (2.997e-08, 5.994e-08, 9e-5, 1e-3),
    "rz": (0.0, 0.0),
    "sx": (2.997e-08, 5.994e-08, 9e-5, 1e-3),
    "x": (2.997e-08, 5.994e-08, 9e-5, 1e-3),
    "u3": (2.997e-08, 5.994e-08, 9e-5, 1e-3),
    "measure": (6.99966e-07, 1.500054e-06, 1e-5, 5e-3),
    "delay": (None, None),
    "reset": (None, None),
}

_NOISE_DEFAULTS_FALLBACK = {
    "1-q": (2.997e-08, 5.994e-08, 9e-5, 1e-4),
    "multi-q": (7.992e-08, 8.99988e-07, 5e-3),
}

class NoisyFakeBackend(GenericBackendV2):
    def __init__(
        self,
        num_qubits: int,
        basis_gates: list[str] | None = None,
        *,
        coupling_map: list[list[int]] | CouplingMap | None = None,
        control_flow: bool = False,
        calibrate_instructions: bool | InstructionScheduleMap | None = None,
        dtm: float | None = None,
        seed: int | None = None,
        noise_settings: dict,
    ):
        self._noise_settings = noise_settings
        self.basis_gates = basis_gates
        super().__init__(num_qubits,
            basis_gates,
            coupling_map=coupling_map,
            control_flow=control_flow,
            calibrate_instructions=calibrate_instructions,
            dtm=dtm,
            seed=seed)

    def _get_noise_defaults(self, name: str, num_qubits: int) -> tuple:
        if name in self._noise_settings:
            return self._noise_settings[name]
        if name in _NOISE_DEFAULTS:
            return _NOISE_DEFAULTS[name]
        if num_qubits == 1:
            return _NOISE_DEFAULTS_FALLBACK["1-q"]
        return _NOISE_DEFAULTS_FALLBACK["multi-q"]

    def _build_generic_target_self(self):
        self._target = Target(
            description=f"Generic Target with {self._num_qubits} qubits",
            num_qubits=self._num_qubits,
            dt=0.222e-9,
            qubit_properties=[
                QubitProperties(
                    t1=self._noise_settings["t1"],
                    t2=self._noise_settings["t2"],
                    frequency=5e9
                )
                for _ in range(self._num_qubits)
            ],
            concurrent_measurements=[list(range(self._num_qubits))]
        )
        calibration_inst_map = None
        if self._calibrate_instructions is not None:
            if isinstance(self._calibrate_instructions, InstructionScheduleMap):
                calibration_inst_map = self._calibrate_instructions
            else:
                defaults = self._generate_calibration_defaults()
                calibration_inst_map = defaults.instruction_schedule_map
        for name in self._basis_gates:
            if name not in self._supported_gates:
                raise QiskitError(
                    f"Provided basis gate {name} is not an instruction "
                    f"in the standard qiskit circuit library."
                )
            gate = self._supported_gates[name]
            noise_params = self._get_noise_defaults(name, gate.num_qubits)
            self._add_noisy_instruction_to_target(gate, noise_params, calibration_inst_map)
        if self._control_flow:
            self._target.add_instruction(IfElseOp, name="if_else")
            self._target.add_instruction(WhileLoopOp, name="while_loop")
            self._target.add_instruction(ForLoopOp, name="for_loop")
            self._target.add_instruction(SwitchCaseOp, name="switch_case")
            self._target.add_instruction(BreakLoopOp, name="break")
            self._target.add_instruction(ContinueLoopOp, name="continue")

def _get_heavy_hex_row_qubit_id(row, column, num_qubits_row, num_qubits_between_rows):
    if row == 0:
        return column
    return (row - 1) * num_qubits_row + num_qubits_row - 2 + row * num_qubits_between_rows + column
    
def _get_heavy_hex_bridge_qubit_id(row, column, num_qubits_row, num_qubits_between_rows):
    offset = int(column / 4) if row % 2 == 0 else int((column - 2) / 4)
    last_column = num_qubits_row - 3 if row == 0 else num_qubits_row - 1
    return _get_heavy_hex_row_qubit_id(row, last_column, num_qubits_row, num_qubits_between_rows) + offset + 1

def create_fake_heavy_hex_backend(
    rows,
    columns,
    one_qubit_gate_duration=5e-10,
    one_qubit_gate_error=0.001,
    two_qubit_gate_duration=2e-10,
    two_qubit_gate_error=0.005,
    readout_duration=5e-10,
    readout_error=0.001,
    t1=100,
    t2=1.5,
) -> NoisyFakeBackend:
    noise_settings = {
        "ecr": (two_qubit_gate_duration, two_qubit_gate_error),
        "cz": (two_qubit_gate_duration, two_qubit_gate_error),
        "rz": (one_qubit_gate_duration, one_qubit_gate_error),
        "sx": (one_qubit_gate_duration, one_qubit_gate_error),
        "x": (one_qubit_gate_duration, one_qubit_gate_error),
        "id": (one_qubit_gate_duration, one_qubit_gate_error),
        "u3": (one_qubit_gate_duration, one_qubit_gate_error),
        "delay": (0, 0),
        "reset": (0, 0),
        "measure": (readout_duration, readout_error),
        "t1": t1,
        "t2": t2
    }
    basis_gates=["id", "rz", "sx", "x", "u3", "cz", "ecr", "reset", "delay", "measure"]
    num_qubits_row = 4 * columns + 3
    num_qubits_between_rows = columns + 1
    num_qubits = _get_heavy_hex_row_qubit_id(rows, num_qubits_row - 3, num_qubits_row, num_qubits_between_rows) + 1
    coupling_map = []
    for r in range(rows + 1):
        num_qubits_current_row = num_qubits_row - 2 if r == 0 or r == rows else num_qubits_row
        for c in range(num_qubits_current_row):
            qubit_id = _get_heavy_hex_row_qubit_id(r, c, num_qubits_row, num_qubits_between_rows)
            if c + 1 < num_qubits_current_row:
                coupling_map.append([qubit_id, qubit_id + 1])
            offset = 0
            if r % 2 == 1:
                offset = -2
            if (c + offset) % 4 == 0 and r < rows:
                bridge_qubit_id = _get_heavy_hex_bridge_qubit_id(r, c, num_qubits_row, num_qubits_between_rows)
                next_c = c if r < rows - 1 else c - 2
                next_qubit_id = _get_heavy_hex_row_qubit_id(r + 1, next_c, num_qubits_row, num_qubits_between_rows)
                coupling_map.append([qubit_id, bridge_qubit_id])
                coupling_map.append([bridge_qubit_id, next_qubit_id])
    return NoisyFakeBackend(num_qubits, basis_gates=basis_gates, coupling_map=coupling_map, noise_settings=noise_settings)