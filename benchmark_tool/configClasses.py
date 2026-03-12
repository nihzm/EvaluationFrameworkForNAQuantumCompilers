"""
Configuration and Data Classes for Benchmark Tool
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class CompilerConfig:
    """
    Configuration for a specific compiler
    """
    name: str
    path: str
    executable: str
    benchmarks: str
    description: str
    supportedFeatures: List[str]
    requirements: List[str]
    resultDir: str
    pythonExecutable: str
    archJson: str


@dataclass
class BenchmarkConfig:
    """
    Configuration for a benchmark run
    """
    compilers: List[str]
    benchmarkSets: List[str]
    outputDir: str
    numRuns: int = 1
    timeout: int = 300  # seconds
    arch: Path


@dataclass
class BenchmarkResult:
    """
    Result of a single benchmark run
    """
    compilerName: str
    benchmarkName: str
    runId: int
    success: bool
    metrics: Dict[str, float]
    errorMessage: Optional[str] = None
    executionTime: float = 0.0
    timestamp: str = ""
