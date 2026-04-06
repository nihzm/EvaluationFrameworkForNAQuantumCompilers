# hardware parameters based on Rubidium setup from https://iopscience.iop.org/article/10.1088/2058-9565/ad33ac
defaults = {
    "U3_GATE_FIDELITY": 0.999,
    "U3_GATE_DURATION": 0.5, # in microseconds
    "CZ_GATE_FIDELITY": 0.995,
    "CZ_GATE_DURATION": 0.2, # in microseconds
    "CCZ_GATE_FIDELITY": 0.98,
    "CCZ_GATE_DURATION": 1, # in microseconds
    "QUBIT_DECAY":  1e08, # t1 in microseconds 
    "QUBIT_DEPHASING": 1.5e06, # t2 in microseconds
    "SHUTTLING_FIDELITY": 1.0,
    "SHUTTLING_SPEED": 0.55, # in micrometers/microseconds
    "TRAP_SWAP_DURATION": 20,
    "TRAP_SWAP_FIDELITY": 1.0,
    "INTERACTION_RADIUS": 2.0, # in micrometers
    "RESTRICTION_RADIUS": 4.0, # in micrometers
    "TRAP_TRANSFER_PROXIMITY": 1e-05, # in micrometers
    "AOD_BEAM_PROXIMITY": 1e-03 # in micrometers
}

class FPQAConfig:
    def __init__(self, config: dict):
        for key in defaults:
            if key in config:
                setattr(self, key, config[key])
            else:
                setattr(self, key, defaults[key])

    def to_string(self):
        config = {}
        for key in defaults:
            config[key] = getattr(self, key)
        return str(config)
                