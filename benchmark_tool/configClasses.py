"""
Configuration and Data Classes for Benchmark Tool
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class CompilerConfig:
    """
    Configuration for a specific compiler
    """
    name: str
    path: str
    description: str
    resultDir: str
    pythonExecutable: str
    archJson: str
    qasm: bool


@dataclass
class BenchmarkConfig:
    """
    Configuration for a benchmark run
    """
    compilers: List[str]
    benchmarkSet: Path
    outputDir: Path
    arch: Path
    cnf: bool
    numRuns: int = 1
    timeout: int = 300  # seconds
