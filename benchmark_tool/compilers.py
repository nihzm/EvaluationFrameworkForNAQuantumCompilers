"""
Compiler Interface and Base Classes
"""

import logging
import os
import time
import subprocess
import json
from typing import Dict
from pathlib import Path

from configClasses import CompilerConfig


class CompilerInterface:
    """
    Abstract interface for interacting with different compilers
    Attributes:
        config (CompilerConfig): Compiler configuration
        logger (logging.Logger): Logger for compiler interface  
    """

    def __init__(self, config: CompilerConfig):
        self.config = config
        self.logger = logging.getLogger(f"Compiler.{config.name}")

    def compileCircuit(self, circuitFile: str):
        """
        Compile a circuit and return metrics

        Args:
            circuitFile: Path to input circuit (QASM or other format)

        Returns:
            Dictionary with compilation metrics
        """
        raise NotImplementedError


class ParallaxCompiler(CompilerInterface):
    """
    Interface for Parallax compiler
    """

    def compileCircuit(self, circuitFile: str):

        arch = json.loads(self.config.archJson)
        archParams = arch.get("architecture", {})
        hwSpec = arch.get("hardware_spec", {})

        cmd = [
            self.config.pythonExecutable,
            os.path.join(self.config.path, "run.py"),
            "--circuit", circuitFile,
            "--result-dir", self.config.resultDir,
            "--array-width", str(archParams.get("array_width")),
            "--array-height", str(archParams.get("array_height")),
            "--aod-columns", str(archParams.get("aod_columns")),
            "--aod-rows", str(archParams.get("aod_rows")),
            "--radius", str(hwSpec.get("R_B"))
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.stdout:
            self.logger.info(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            self.logger.error(f"STDERR:\n{result.stderr}")


class EnolaCompiler(CompilerInterface):
    """
    Interface for Enola compiler
    """

    def compileCircuit(self, circuitFile: str):

        arch = json.loads(self.config.archJson)
        archParams = arch.get("architecture", {})
        strategySpec = arch.get("strategy_spec", {})

        cmd = [
            self.config.pythonExecutable,
            os.path.join(self.config.path, "run_qasm.py"),
            "--circuit", circuitFile,
            "--result-dir", self.config.resultDir,
            "--array-width", str(archParams.get("array_width")),
            "--array-height", str(archParams.get("array_height")),
            "--aod-columns", str(archParams.get("aod_columns")),
            "--aod-rows", str(archParams.get("aod_rows")),
            "--routing-strategy", strategySpec.get("routing_strategy"),
            "--r2i", str(strategySpec.get("r2i")),
            "--dependency", str(strategySpec.get("dependency")),
            "--use-window", str(strategySpec.get("use_window")),
            "--full-code", str(strategySpec.get("full_code")),
            "--trivial-layout", str(strategySpec.get("trivial_layout"))
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.stdout:
            self.logger.info(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            self.logger.error(f"STDERR:\n{result.stderr}")


class DasAtomCompiler(CompilerInterface):
    """
    Interface for DasAtom compiler
    """

    def compileCircuit(self, circuitFile: str):
        cmd = [
            self.config.pythonExecutable,
            os.path.join(self.config.path, "run.py"),
            "--circuit", circuitFile,
            "--result-dir", self.config.resultDir,
            "--arch", self.config.archJson
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.stdout:
            self.logger.info(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            self.logger.error(f"STDERR:\n{result.stderr}")


class ZACCompiler(CompilerInterface):
    """
    Interface for ZAC compiler
    """

    def compileCircuit(self, circuitFile: str):

        trimmedCircuit = self._trimMeasurements(circuitFile)

        cmd = [
            self.config.pythonExecutable,
            os.path.join(self.config.path, "run.py"),
            "--circuit", trimmedCircuit,
            "--zac",
            "--result-dir", self.config.resultDir,
            "--arch", self.config.archJson
            # TODO add architecture specification (curr)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.stdout:
            self.logger.info(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            self.logger.error(f"STDERR:\n{result.stderr}")

        try:
            os.remove(trimmedCircuit)
            self.logger.info(f"Deleted trimmed circuit file: {trimmedCircuit}")
        except OSError as e:
            self.logger.warning(f"Could not delete trimmed file: {e}")
    

    def _trimMeasurements(self, circuitFile: str) -> Dict:
        with open(circuitFile, 'r') as f:
            lines = f.readlines()
    
        # Filter out measure lines
        filteredLines = [line for line in lines if 'measure' not in line.lower()]
        
        # Create output file path
        base, ext = os.path.splitext(circuitFile)
        outputFile = f"{base}_trimmed{ext}"
        
        # Write filtered content
        with open(outputFile, 'w') as f:
            f.writelines(filteredLines)

        self.logger.info(f"Trimmed circuit saved to {outputFile}")
        return outputFile


class WeaverCompiler(CompilerInterface):
    """
    Interface for Weaver compiler
    """

    def compileCircuit(self, circuitFile: str):
        cmd = [
            self.config.pythonExecutable,
            os.path.join(self.config.path, "run.py"),
            "--circuit", circuitFile,
            "--result-dir", self.config.resultDir,
            "--arch", self.config.archJson
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)


class NALACCompiler(CompilerInterface):
    """
    Interface for NALAC compiler
    """

    def compileCircuit(self, circuitFile: str):

        trimmedCircuit = self._trimMeasurements(circuitFile)

        cmd = [
            self.config.pythonExecutable,
            os.path.join(self.config.path, "run.py"),
            "--circuit", trimmedCircuit,
            "--result-dir", self.config.resultDir,
            "--arch", self.config.archJson
            #TODO add architecture specification
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.stdout:
            self.logger.info(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            self.logger.error(f"STDERR:\n{result.stderr}")

        try:
            os.remove(trimmedCircuit)
            self.logger.info(f"Deleted trimmed circuit file: {trimmedCircuit}")
        except OSError as e:
            self.logger.warning(f"Could not delete trimmed file: {e}")
    

    def _trimMeasurements(self, circuitFile: str) -> Dict:
        with open(circuitFile, 'r') as f:
            lines = f.readlines()
    
        # Filter out measure lines
        filteredLines = [line for line in lines if 'measure' not in line.lower()]
        
        # Create output file path
        base, ext = os.path.splitext(circuitFile)
        outputFile = f"{base}_trimmed{ext}"
        
        # Write filtered content
        with open(outputFile, 'w') as f:
            f.writelines(filteredLines)

        self.logger.info(f"Trimmed circuit saved to {outputFile}")
        return outputFile