"""
Compiler Registry

Maps compiler names to their implementations and configurations
"""

from compilers import (
    ParallaxCompiler,
    ZACCompiler,
    WeaverCompiler,
    NALACCompiler,
    EnolaCompiler,
    DasAtomCompiler
)

COMPILER_REGISTRY = {
    "parallax": {
        "class": ParallaxCompiler,
        "path": "../compilers/Parallax",
        "description": "Parallax Compiler for Neutral Atom Quantum Computers",
        "benchmarks": "qasm",
    },
    "zac": {
        "class": ZACCompiler,
        "path": "../compilers/QMap",
        "description": "ZAC Compiler for Zoned Architectures",
        "benchmarks": "qasm"
    },
    "weaver": {
        "class": WeaverCompiler,
        "path": "../compilers/Weaver",
        "description": "Weaver Compiler for Neutral Atom Systems",
        "benchmarks": "max3sat"
    },
    "nalac": {
        "class": NALACCompiler,
        "path": "../compilers/QMap",
        "description": "NALAC Compiler for Neutral Atom Lattice Architectures",
        "benchmarks": "qasm"
    },
    "enola": {
        "class": EnolaCompiler,
        "path": "../compilers/Enola",
        "description": "Enola Compiler for Rydberg Atom Systems",
        "benchmarks": "qasm"    
    },
    "dasatom": {
        "class": DasAtomCompiler,
        "path": "../compilers/DasAtom",
        "description": "DasAtom Compiler for Rydberg Atom Systems",
        "benchmarks": "qasm"
    }
}
