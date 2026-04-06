"""
Benchmark Manager

Orchestrates benchmark execution across multiple compilers
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from configClasses import BenchmarkConfig, CompilerConfig
from registry import COMPILER_REGISTRY

class BenchmarkManager:
    """
    Orchestrates benchmark execution across multiple compilers
    Attributes:
        config (BenchmarkConfig): Benchmark configuration
        logger (logging.Logger): Logger for benchmark manager
        compilers (Dict): Initialized compiler interfaces
        results (List[BenchmarkResult]): Collected benchmark results
    """

    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.logger = logging.getLogger("BenchmarkManager")
        self.compilers: Dict = {}
        self._configureLogging()
        self._setupOutputDir()


    def _configureLogging(self):
        """
        Configure logging for benchmark manager - logs are saved in benchmark_<timestamp>.log file to output/logs directory
        """

        logFormat = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        logFilename = f"benchmark_{timestamp}.log"
        logFilePath = os.path.join(self.config.outputDir, "logs", logFilename)
        
        logging.basicConfig(
            level=logging.INFO,
            format=logFormat,
            handlers=[
                logging.FileHandler(logFilePath),
                logging.StreamHandler(),
            ]
        )


    def _setupOutputDir(self):
        """
        Create output directory structure :
        - circuits/
        - logs/
        - metrics/
        """

        Path(self.config.outputDir).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(self.config.outputDir, "circuits")).mkdir(exist_ok=True)
        Path(os.path.join(self.config.outputDir, "logs")).mkdir(exist_ok=True)
        Path(os.path.join(self.config.outputDir, "metrics")).mkdir(exist_ok=True)


    def initializeCompilers(self) -> bool:
        """
        Initialize and validate all requested compilers - returns True if all compilers initialized successfully
        """

        self.logger.info(f"Initializing {len(self.config.compilers)} compilers...")

        archJson = self._loadArchitectureJson(self.config.arch)

        for compilerName in self.config.compilers:

            # Check if compiler is registered
            if compilerName not in COMPILER_REGISTRY:
                self.logger.error(f"Unknown compiler: {compilerName}")
                continue

            try:
                # Configure compiler
                compilerInfo = COMPILER_REGISTRY[compilerName]

                config = CompilerConfig(
                    name=compilerName,
                    path=compilerInfo["path"],
                    description=compilerInfo["description"],
                    resultDir=os.path.join(self.config.outputDir, "circuits", compilerName),
                    pythonExecutable=os.path.join(compilerInfo["path"], "venv", "bin", "python"),
                    archJson=archJson,
                    qasm=compilerInfo["qasm"]
                )

                self.logger.info(f"Output directory for {compilerName}: {config.resultDir}")

                # Instantiate compiler interface
                compiler = compilerInfo["class"](config)

                self.compilers[compilerName] = compiler

            except Exception as e:
                self.logger.error(f"Failed to initialize {compilerName}: {e}")

        return len(self.compilers) == len(self.config.compilers)


    def _loadArchitectureJson(self, archPath: Path) -> str:
        """
        Load architecture JSON from file and return it as normalized JSON string.
        """

        try:
            with archPath.open("r", encoding="utf-8") as f:
                archData = json.load(f)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Architecture file not found: {archPath}") from e
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in architecture file '{archPath}': {e}") from e

        return json.dumps(archData)


    def runBenchmarks(self):
        """
        Execute all benchmarks on all compilers in the managers compiler list for the specified number of runs
        """

        if not self.compilers:
            self.logger.error("No compilers initialized. Exiting.")
            return

        self.logger.info(f"Starting benchmark execution ...")

        for compilerName, compiler in self.compilers.items():
            benchmarks = self._loadBenchmarks(compiler.config.qasm)

            compilerSummary = self._initCompilerSummary(compilerName)

            for runId in range(self.config.numRuns):
                for benchmark in benchmarks:
                    self.logger.info(f"{compilerName} (run {runId+1}/{self.config.numRuns}) - Running {benchmark}")

                    result = self._runSingleBenchmark(compiler, benchmark)
                    self._appendToCompilerSummary(compilerSummary, result, runId, benchmark)

            self._writeCompilerSummary(compilerName, compilerSummary)


    def _loadBenchmarks(self, qasm: bool) -> List[str]:
        """
        Load benchmark circuits from the specified benchmark directory - expects .qasm files - returns list of file paths
        """
        benchmark_dir = self.config.benchmarkSet

        if not benchmark_dir.exists():
            self.logger.warning(f"Benchmark directory '{benchmark_dir}' does not exist.")
            raise FileNotFoundError(f"Benchmark directory '{benchmark_dir}' does not exist.")

        if not benchmark_dir.is_dir():
            self.logger.warning(f"Benchmark path '{benchmark_dir}' is not a directory.")
            raise NotADirectoryError(f"Benchmark path '{benchmark_dir}' is not a directory.")

        suffix = "*.qasm" if qasm else "*.cnf"
        benchmark_files = sorted(
            f for f in benchmark_dir.rglob(suffix) if f.is_file()
        )

        benchmarks = [str(f) for f in benchmark_files]

        kind = "QASM" if qasm else "CNF"
        self.logger.info(f"Found {len(benchmarks)} {kind} benchmark circuits in '{benchmark_dir}'")
        for b in benchmarks:
            self.logger.info(f"  - {b}")
        return benchmarks


    def _runSingleBenchmark(self, compiler, benchmark: str) -> Dict:
        """
        Execute a single benchmark
        """

        try:
            resultPath = compiler.compileCircuit(benchmark)
            metrics = compiler.extractMetrics(resultPath)
            return metrics

        except Exception as e:
            self.logger.error(f"Benchmark failed: {e}")


    def _initCompilerSummary(self, compilerName: str) -> Dict:
        """Initialize per-compiler summary payload written after compiler finished."""

        return {
            "compiler": compilerName,
            "benchmarks": [],
            "runs": {}
        }


    def _appendToCompilerSummary(self, summary: Dict, metrics: Dict, runId: int, benchmarkName: str):
        """Append a single benchmark result to list-based summary structure."""
        summary["benchmarks"].append(benchmarkName)
        metrics = metrics or {}

        if runId not in summary["runs"]:
            summary["runs"][runId] = {}

        for metricName in metrics.keys():
            if metricName not in summary["runs"][runId]:
                summary["runs"][runId][metricName] = []
            summary["runs"][runId][metricName].append(metrics[metricName])


    def _writeCompilerSummary(self, compilerName: str, summary: Dict):
        """Write summary JSON to results/metrics/<arch-file-stem>/<compiler>.json."""
        archFolderName = self.config.arch.stem
        metricsDir = Path(self.config.outputDir) / "metrics" / archFolderName
        metricsDir.mkdir(parents=True, exist_ok=True)

        outputPath = metricsDir / f"{compilerName}.json"
        with outputPath.open("w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        self.logger.info(f"Wrote metrics summary for {compilerName}: {outputPath}")
