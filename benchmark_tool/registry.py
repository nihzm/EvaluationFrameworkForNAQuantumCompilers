"""
Compiler Registry

Maps compiler names to their implementations and configurations
"""

from compilers import (
    ParallaxCompiler,
    ZACCompiler,
    NALACCompiler,
    EnolaCompiler,
    WeaverCompiler
)

PARAMETER_CATALOG = {
    "architecture.array_width": {
        "type": int,
        "prompt": "Array width",
        "description": "Number of columns in the atom array",
    },
    "architecture.array_height": {
        "type": int,
        "prompt": "Array height",
        "description": "Number of rows in the atom array",
    },
    "architecture.aod_columns": {
        "type": int,
        "prompt": "AOD columns",
        "description": "Number of AOD-controlled columns",
    },
    "architecture.aod_rows": {
        "type": int,
        "prompt": "AOD rows",
        "description": "Number of AOD-controlled rows",
    },



    "hardware_spec.rydberg_interaction_range": {
        "type": float,
        "prompt": "Rydberg interaction range",
        "description": "Distance over which Rydberg interactions occur",
    },
    "hardware_spec.blockade_radius_factor": {
        "type": float,
        "prompt": "Blockade radius factor",
        "description": "Factor by which the blockade radius is scaled",
    },
    "hardware_spec.aod_site_separation": {
        "type": float,
        "prompt": "Minimum AOD separation",
        "description": "Minimum distance between AOD-controlled sites",
    },
    "hardware_spec.slm_site_separation": {
        "type": float,
        "prompt": "SLM site separation",
        "description": "Distance between SLM sites",
    },



    "duration_spec.rydberg_gate_duration": {
        "type": float,
        "prompt": "Rydberg gate duration",
        "description": "Duration of Rydberg gates",
    },
    "duration_spec.atom_transfer_duration": {
        "type": float,
        "prompt": "Atom transfer duration",
        "description": "Time required to transfer atoms between sites",
    },
    "duration_spec.single_qubit_gate_duration": {
        "type": float,
        "prompt": "Single-qubit gate duration",
        "description": "Duration of single-qubit gates",
    },
    "duration_spec.shuttling_speed": {
        "type": float,
        "prompt": "Shuttling speed",
        "description": "Speed of shuttling operations in micrometers per microsecond",
    },


    "fidelity_spec.rydberg_gate_fidelity": {
        "type": float,
        "prompt": "Rydberg gate fidelity",
        "description": "Fidelity of Rydberg gates",
    },
    "fidelity_spec.single_qubit_gate_fidelity": {
        "type": float,
        "prompt": "Single-qubit gate fidelity",
        "description": "Fidelity of single-qubit gates",
    },
    "fidelity_spec.atom_transfer_fidelity": {
        "type": float,
        "prompt": "Atom transfer fidelity",
        "description": "Fidelity of atom transfer operations",
    },
    "fidelity_spec.shuttling_fidelity": {
        "type": float,
        "prompt": "Shuttling fidelity",
        "description": "Fidelity of shuttling operations",
    },
    "fidelity_spec.T1": {
        "type": float,
        "prompt": "Coherence time T1",
        "description": "Time during which qubits maintain their energy state",
    },
    "fidelity_spec.T2": {
        "type": float,
        "prompt": "Coherence time T2",
        "description": "Time during which qubits maintain their quantum state",
    },

    "tolerance_spec.trap_transfer_proximity": {
        "type": float,
        "prompt": "Trap transfer proximity",
        "description": "Proximity threshold for trap transfer operations in micrometers",
    },
    "tolerance_spec.aod_beam_proximity": {
        "type": float,
        "prompt": "AOD beam proximity",
        "description": "Proximity threshold for AOD beam operations in micrometers",
    },

    "strategy_spec.routing_strategy": {
        "type": str,
        "prompt": "Routing strategy",
        "description": "Strategy for routing quantum gates through the hardware",
    },
    "strategy_spec.r2i": {
        "type": bool,
        "prompt": "Enable R2I",
        "description": "Whether to enable the R2I (Rydberg to Interaction) optimization",
    },
    "strategy_spec.dependency": {
        "type": bool,
        "prompt": "Enable dependency-aware scheduling",
        "description": "Whether to enable dependency-aware scheduling",
    },
    "strategy_spec.use_window": {
        "type": bool,
        "prompt": "Use windowing",
        "description": "Whether to use windowing for scheduling",
    },
    "strategy_spec.full_code": {
        "type": bool,
        "prompt": "Use full code mode",
        "description": "Whether to use full code mode",
    },
    "strategy_spec.trivial_layout": {
        "type": bool,
        "prompt": "Use trivial layout",
        "description": "Whether to use trivial layout",
    },
}

COMPILER_REGISTRY = {
    "parallax": {
        "class": ParallaxCompiler,
        "path": "../compilers/Parallax",
        "description": "Parallax Compiler for Neutral Atom Quantum Computers",
        "qasm": True,
        "required_parameters": [
            "architecture.array_width",
            "architecture.array_height",
            "architecture.aod_columns",
            "architecture.aod_rows",
            "hardware_spec.rydberg_interaction_range",
        ],
    },
    "zac": {
        "class": ZACCompiler,
        "path": "../compilers/QMap",
        "description": "ZAC Compiler for Zoned Architectures",
        "qasm": True,
        "required_parameters": [
            "architecture.array_width",
            "architecture.array_height",
            "architecture.aod_columns",
            "architecture.aod_rows",
            "hardware_spec.slm_site_separation",
            "hardware_spec.aod_site_separation",
            "duration_spec.rydberg_gate_duration",
            "duration_spec.single_qubit_gate_duration",
            "duration_spec.atom_transfer_duration",
            "fidelity_spec.rydberg_gate_fidelity",
            "fidelity_spec.single_qubit_gate_fidelity",
            "fidelity_spec.atom_transfer_fidelity",
            "fidelity_spec.T2"
        ],
    },
    "nalac": {
        "class": NALACCompiler,
        "path": "../compilers/QMap",
        "description": "NALAC Compiler for Neutral Atom Lattice Architectures",
        "qasm": True,
        "required_parameters": [
            "architecture.array_width",
            "architecture.array_height",
            "architecture.aod_columns",
            "architecture.aod_rows",
            "hardware_spec.slm_site_separation",
            "hardware_spec.aod_site_separation",
            "duration_spec.rydberg_gate_duration",
            "duration_spec.single_qubit_gate_duration",
            "duration_spec.atom_transfer_duration",
            "fidelity_spec.rydberg_gate_fidelity",
            "fidelity_spec.single_qubit_gate_fidelity",
            "fidelity_spec.atom_transfer_fidelity",
            "fidelity_spec.T2"
        ],
    },
    "enola": {
        "class": EnolaCompiler,
        "path": "../compilers/Enola",
        "description": "Enola Compiler for Rydberg Atom Systems",
        "qasm": True,
        "required_parameters": [
            "architecture.array_width",
            "architecture.array_height",
            "architecture.aod_columns",
            "architecture.aod_rows",
            "strategy_spec.routing_strategy",
            "strategy_spec.r2i",
            "strategy_spec.dependency",
            "strategy_spec.use_window",
            "strategy_spec.full_code",
            "strategy_spec.trivial_layout"
        ],    
    },
    "weaver": {
        "class": WeaverCompiler,
        "path": "../compilers/Weaver",
        "description": "Weaver Compiler for Quantum Circuits",
        "qasm": False,
        "required_parameters": [
            "hardware_spec.rydberg_interaction_range",
            "hardware_spec.blockade_radius_factor",
            "duration_spec.rydberg_gate_duration",
            "duration_spec.single_qubit_gate_duration",
            "duration_spec.atom_transfer_duration",
            "duration_spec.shuttling_speed",
            "fidelity_spec.rydberg_gate_fidelity",
            "fidelity_spec.single_qubit_gate_fidelity",
            "fidelity_spec.atom_transfer_fidelity",
            "fidelity_spec.shuttling_fidelity",
            "fidelity_spec.T1",
            "fidelity_spec.T2",
            "tolerance_spec.trap_transfer_proximity",
            "tolerance_spec.aod_beam_proximity"
        ],
    }
}