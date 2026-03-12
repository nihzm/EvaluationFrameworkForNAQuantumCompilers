"""
Benchmark Manager

Orchestrates benchmark execution across multiple compilers
"""

import json
import logging
import os
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from configClasses import BenchmarkConfig, BenchmarkResult, CompilerConfig
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
        self.results: List[BenchmarkResult] = []
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
        """

        Path(self.config.outputDir).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(self.config.outputDir, "circuits")).mkdir(exist_ok=True)
        Path(os.path.join(self.config.outputDir, "logs")).mkdir(exist_ok=True)


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
                    executable="",  # To be filled by subclass
                    benchmarks=compilerInfo["benchmarks"],
                    description=compilerInfo["description"],
                    supportedFeatures=[],  # To be filled by subclass
                    requirements=[],  # To be filled by subclass
                    resultDir=os.path.join(self.config.outputDir, "circuits", compilerName),
                    pythonExecutable=os.path.join(compilerInfo["path"], "venv", "bin", "python"),
                    archJson=archJson
                )

                # Instantiate compiler interface
                compiler = compilerInfo["class"](config)

                self.compilers[compilerName] = compiler
                # Validate installation #TODO (then remove line above)
                #if compiler.validateInstallation():
                #    self.compilers[compilerName] = compiler
                #   self.logger.info(f"✓ {compilerName} initialized successfully")
                #else:
                #    self.logger.warning(f"✗ {compilerName} validation failed")

            except Exception as e:
                self.logger.error(f"Failed to initialize {compilerName}: {e}")

        return len(self.compilers) == len(self.config.compilers)


    def _loadArchitectureJson(self, archPath) -> str:
        """
        Load architecture JSON from file and return it as normalized JSON string.
        """

        path = Path(archPath)
        try:
            with path.open("r", encoding="utf-8") as f:
                archData = json.load(f)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Architecture file not found: {path}") from e
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in architecture file '{path}': {e}") from e

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

            benchmarks = self._loadBenchmarks(compiler.config.benchmarks)

            for runId in range(self.config.numRuns):

                for benchmark in benchmarks:

                    self.logger.info(f"{compilerName} (run {runId+1}/{self.config.numRuns}) - Running {benchmark}")

                    result = self._runSingleBenchmark(compilerName, compiler, benchmark, runId)
                    self.results.append(result)


    def _loadBenchmarks(self, subDir: str) -> List[str]:
        """
        Load benchmark circuits based on the specified benchmark sets
        """
        benchmarks = []

        for benchmarkName in self.config.benchmarkSets:

            benchmarkDir = Path("./benchmarks")

            if benchmarkDir.exists():

                # Load from benchmarks directory all .qasm / .cnf files (dependent on passed subDir string)
                files = list(benchmarkDir.glob(f"**/{subDir}/*"))

                if benchmarkName == "all":

                    benchmarks.extend([str(f) for f in files])

                    self.logger.info(f"Found {len(files)} benchmark circuits in ./benchmarks")
                    break  # 'all' includes everything, no need to check other sets

                else:
                    # Filter files for specific benchmark set
                    filteredFiles = [f for f in files if benchmarkName in f.name]
                    benchmarks.extend([str(f) for f in filteredFiles])

                    self.logger.info(f"Found {len(filteredFiles)} benchmark circuits for set '{benchmarkName}' in ./benchmarks")

            else:
                self.logger.warning("Benchmark directory './benchmarks' does not exist.")
                raise FileNotFoundError("Benchmark directory './benchmarks' does not exist.")

        self.logger.info(f"Loaded {len(benchmarks)} benchmark circuits")

        return benchmarks


    # TODO TODO TODO
    def _runSingleBenchmark(self, compilerName: str, compiler, benchmark: str, runIndex: int) -> BenchmarkResult:
        """
        Execute a single benchmark
        """
        result = BenchmarkResult( #TODO maybe dont need that but lets do this trimming later
            compilerName=compilerName,
            benchmarkName=benchmark,
            runId=runIndex,
            success=False,
            metrics={},
            timestamp=datetime.now().isoformat(),
        )

        try:
            compilationResult = compiler.compileCircuit(benchmark)
            #TODO: extract metrics from compilationResult
            result.success = True

        except Exception as e:
            result.success = False
            result.errorMessage = str(e)
            self.logger.error(f"Benchmark failed: {e}")

        return result
