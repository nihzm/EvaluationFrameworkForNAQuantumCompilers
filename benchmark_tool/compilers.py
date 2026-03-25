"""Compiler interfaces and metric extraction."""

import ast
import json
import logging
import math
import os
import re
import subprocess
from typing import Dict, List, Optional

from configClasses import CompilerConfig


class CompilerInterface:
    def __init__(self, config: CompilerConfig):
        self.config = config
        self.logger = logging.getLogger(f"Compiler.{config.name}")

    def compileCircuit(self, circuitFile: str):
        raise NotImplementedError

    def extractMetrics(self, resultFilePath: str) -> Dict:
        raise NotImplementedError


class ParallaxCompiler(CompilerInterface):
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
            "--radius", str(hwSpec.get("rydberg_interaction_range")),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.stdout:
            self.logger.info(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            self.logger.error(f"STDERR:\n{result.stderr}")

        resultFilePath = self.getResultFilePath(circuitFile)
        if not os.path.exists(resultFilePath):
            self.logger.warning(f"Parallax result file not found: {resultFilePath}")
            return None
        return resultFilePath

    def getResultFilePath(self, circuitFile: str) -> str:
        base = os.path.splitext(os.path.basename(circuitFile))[0]
        return os.path.join(self.config.resultDir, f"{base}_result.txt")

    def _parseInstructions(self, resultFilePath: str) -> List[tuple]:
        instructions = []
        with open(resultFilePath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    instructions.append(ast.literal_eval(line))
                except (ValueError, SyntaxError):
                    self.logger.warning(f"Could not parse instruction line: {line!r}")
        return instructions

    def _countMoveOps(self, instructions: List[tuple]) -> int:
        return sum(1 for instr in instructions if instr[1] == "move")

    def _sumMovingDistance(self, instructions: List[tuple]) -> float:
        return sum(instr[6] for instr in instructions if instr[1] == "move")

    def _countTrapSwaps(self, instructions: List[tuple]) -> int:
        return sum(1 for instr in instructions if instr[1] == "load_aod")

    def _countRydbergActivations(self, instructions: List[tuple]) -> int:
        return sum(1 for instr in instructions if instr[1] == "gate_2q")

    def _calcFidelity(self, instructions: List[tuple]) -> float:
        arch = json.loads(self.config.archJson)
        fidelitySpec = arch.get("fidelity_spec", {})
        rydbergGateFidelity = fidelitySpec.get("rydberg_gate_fidelity", 1.0)
        singleQubitGateFidelity = fidelitySpec.get("single_qubit_gate_fidelity", 1.0)
        atomTransferFidelity = fidelitySpec.get("atom_transfer_fidelity", 1.0)

        numberRydbergGates = sum(1 for instr in instructions if instr[1] == "gate_2q")
        numberSingleQubitGates = sum(1 for instr in instructions if instr[1] == "gate_1q")
        numberAtomTransfers = sum(1 for instr in instructions if instr[1] == "move")

        return (
            (rydbergGateFidelity ** numberRydbergGates)
            * (singleQubitGateFidelity ** numberSingleQubitGates)
            * (atomTransferFidelity ** numberAtomTransfers)
        )

    def extractMetrics(self, resultFilePath: str) -> Dict:
        instructions = self._parseInstructions(resultFilePath)
        return {
            "move_count": self._countMoveOps(instructions),
            "total_move_dist": self._sumMovingDistance(instructions),
            "trap_swap_count": self._countTrapSwaps(instructions),
            "num_rydberg_activations": self._countRydbergActivations(instructions),
            "fidelity": self._calcFidelity(instructions),
        }


class EnolaCompiler(CompilerInterface):
    def __init__(self, config: CompilerConfig):
        super().__init__(config)
        self.lastCircuitFile: Optional[str] = None

    def compileCircuit(self, circuitFile: str):
        self.lastCircuitFile = circuitFile
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
        ]
        if strategySpec.get("r2i"):
            cmd.append("--r2i")
        if strategySpec.get("dependency"):
            cmd.append("--dependency")
        if strategySpec.get("use_window"):
            cmd.append("--use-window")
        if strategySpec.get("full_code"):
            cmd.append("--full-code")
        if strategySpec.get("trivial_layout"):
            cmd.append("--trivial-layout")

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.stdout:
            self.logger.info(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            self.logger.error(f"STDERR:\n{result.stderr}")

        resultFilePath = self.getResultFilePath(circuitFile)
        if not os.path.exists(resultFilePath):
            self.logger.warning(f"Enola result file not found: {resultFilePath}")
            return None
        return resultFilePath

    def getResultFilePath(self, circuitFile: str) -> str:
        benchmarkNameWithExt = os.path.basename(circuitFile)
        return os.path.join(self.config.resultDir, "code", f"{benchmarkNameWithExt}_code.json")

    def _parseInstructions(self, resultFilePath: str) -> List[Dict]:
        try:
            with open(resultFilePath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Could not load Enola JSON: {e}")
            return []

    def _countMoveOps(self, enolaJson: List[Dict]) -> int:
        moveCount = 0
        for item in enolaJson:
            if item.get("type") == "Move":
                moveCount += len(item.get("cols", [])) + len(item.get("rows", []))
        return moveCount

    def _sumMovingDistance(self, enolaJson: List[Dict]) -> float:
        total = 0.0
        for item in enolaJson:
            if item.get("type") != "Move":
                continue
            for col in item.get("cols", []):
                if col.get("begin") is not None and col.get("end") is not None:
                    total += abs(col["end"] - col["begin"])
            for row in item.get("rows", []):
                if row.get("begin") is not None and row.get("end") is not None:
                    total += abs(row["end"] - row["begin"])
        return total

    def _countTrapSwaps(self, enolaJson: List[Dict]) -> int:
        count = 0
        for item in enolaJson:
            if item.get("type") in ("Activate", "Deactivate"):
                count += len(item.get("pickup_qs", [])) + len(item.get("dropoff_qs", []))
        return count

    def _countRydbergActivations(self, enolaJson: List[Dict]) -> int:
        numGates = 0
        for item in enolaJson:
            if item.get("type") == "Rydberg":
                numGates += len(item.get("gates", []))
        return numGates

    def _countSingleQubitGatesFromCircuit(self, circuitFile: Optional[str]) -> int:
        if not circuitFile or not os.path.exists(circuitFile):
            return 0
        count = 0
        with open(circuitFile, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("//"):
                    continue
                if "//" in stripped:
                    stripped = stripped.split("//", 1)[0].strip()
                    if not stripped:
                        continue
                lowered = stripped.lower()
                if lowered.startswith(("openqasm", "include", "qreg", "creg", "qubit", "bit", "measure", "barrier", "reset", "delay")):
                    continue
                qubits = re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\]", stripped)
                if len(qubits) == 1:
                    count += 1
        return count

    def _calcFidelity(self, enolaJson: List[Dict]) -> float:
        arch = json.loads(self.config.archJson)
        fidelitySpec = arch.get("fidelity_spec", {})
        rydbergGateFidelity = fidelitySpec.get("rydberg_gate_fidelity", 1.0)
        singleQubitGateFidelity = fidelitySpec.get("single_qubit_gate_fidelity", 1.0)
        atomTransferFidelity = fidelitySpec.get("atom_transfer_fidelity", 1.0)

        numberRydbergGates = self._countRydbergActivations(enolaJson)
        numberAtomTransfers = self._countMoveOps(enolaJson) + self._countTrapSwaps(enolaJson)
        numberSingleQubitGates = self._countSingleQubitGatesFromCircuit(self.lastCircuitFile)

        return (
            (rydbergGateFidelity ** numberRydbergGates)
            * (singleQubitGateFidelity ** numberSingleQubitGates)
            * (atomTransferFidelity ** numberAtomTransfers)
        )

    def extractMetrics(self, resultFilePath: str) -> Dict:
        enolaJson = self._parseInstructions(resultFilePath)
        return {
            "move_count": self._countMoveOps(enolaJson),
            "total_move_dist": self._sumMovingDistance(enolaJson),
            "trap_swap_count": self._countTrapSwaps(enolaJson),
            "num_rydberg_activations": self._countRydbergActivations(enolaJson),
            "fidelity": self._calcFidelity(enolaJson),
        }


class _QMapBaseCompiler(CompilerInterface):
    def _parseInstructions(self, resultFilePath: str) -> List[str]:
        instructions: List[str] = []
        with open(resultFilePath, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    instructions.append(stripped)
        return instructions

    def _countMoveOps(self, instructions: List[str]) -> int:
        return sum(1 for line in instructions if line.startswith("@+ move"))

    def _sumMovingDistance(self, instructions: List[str]) -> float:
        atomPos: Dict[str, tuple] = {}
        atomDecl = re.compile(r"^atom\s+\(([-+]?\d*\.?\d+),\s*([-+]?\d*\.?\d+)\)\s+(atom\d+)\s*$")
        movePattern = re.compile(r"^@\+\s+move\s+\(([-+]?\d*\.?\d+),\s*([-+]?\d*\.?\d+)\)\s+(atom\d+)\s*$")
        total = 0.0
        for line in instructions:
            mDecl = atomDecl.match(line)
            if mDecl:
                atomPos[mDecl.group(3)] = (float(mDecl.group(1)), float(mDecl.group(2)))
                continue
            mMove = movePattern.match(line)
            if not mMove:
                continue
            xNew, yNew, atom = float(mMove.group(1)), float(mMove.group(2)), mMove.group(3)
            xOld, yOld = atomPos.get(atom, (xNew, yNew))
            total += math.hypot(xNew - xOld, yNew - yOld)
            atomPos[atom] = (xNew, yNew)
        return total

    def _countTrapSwaps(self, instructions: List[str]) -> int:
        return sum(1 for line in instructions if line.startswith("@+ load") or line.startswith("@+ store"))

    def _countRydbergActivations(self, instructions: List[str]) -> int:
        return sum(1 for line in instructions if line.startswith("@+ cz"))

    def _countSingleQubitGates(self, instructions: List[str]) -> int:
        return sum(1 for line in instructions if line.startswith("@+ u"))

    def _calcFidelity(self, instructions: List[str]) -> float:
        arch = json.loads(self.config.archJson)
        fidelitySpec = arch.get("fidelity_spec", {})
        rydbergGateFidelity = fidelitySpec.get("rydberg_gate_fidelity", 1.0)
        singleQubitGateFidelity = fidelitySpec.get("single_qubit_gate_fidelity", 1.0)
        atomTransferFidelity = fidelitySpec.get("atom_transfer_fidelity", 1.0)
        return (
            (rydbergGateFidelity ** self._countRydbergActivations(instructions))
            * (singleQubitGateFidelity ** self._countSingleQubitGates(instructions))
            * (atomTransferFidelity ** self._countTrapSwaps(instructions))
        )

    def extractMetrics(self, resultFilePath: str) -> Dict:
        instructions = self._parseInstructions(resultFilePath)
        return {
            "move_count": self._countMoveOps(instructions),
            "total_move_dist": self._sumMovingDistance(instructions),
            "trap_swap_count": self._countTrapSwaps(instructions),
            "num_rydberg_activations": self._countRydbergActivations(instructions),
            "fidelity": self._calcFidelity(instructions),
        }


class ZACCompiler(_QMapBaseCompiler):
    def compileCircuit(self, circuitFile: str):
        arch = json.loads(self.config.archJson)
        archParams = arch.get("architecture", {})
        hardwareSpec = arch.get("hardware_spec", {})
        durationSpec = arch.get("duration_spec", {})
        fidelitySpec = arch.get("fidelity_spec", {})

        cmd = [
            self.config.pythonExecutable,
            os.path.join(self.config.path, "run.py"),
            "--circuit", circuitFile,
            "--zac",
            "--result-dir", self.config.resultDir,
            "--array-width", str(archParams.get("array_width")),
            "--array-height", str(archParams.get("array_height")),
            "--aod-columns", str(archParams.get("aod_columns")),
            "--aod-rows", str(archParams.get("aod_rows")),
            "--slm-site-separation", str(hardwareSpec.get("slm_site_separation")),
            "--aod-site-separation", str(hardwareSpec.get("aod_site_separation")),
            "--rydberg-gate-duration", str(durationSpec.get("rydberg_gate_duration")),
            "--single-qubit-gate-duration", str(durationSpec.get("single_qubit_gate_duration")),
            "--atom-transfer-duration", str(durationSpec.get("atom_transfer_duration")),
            "--rydberg-gate-fidelity", str(fidelitySpec.get("rydberg_gate_fidelity")),
            "--single-qubit-gate-fidelity", str(fidelitySpec.get("single_qubit_gate_fidelity")),
            "--atom-transfer-fidelity", str(fidelitySpec.get("atom_transfer_fidelity")),
            "--qubit-coherence-time", str(fidelitySpec.get("T2")),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.stdout:
            self.logger.info(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            self.logger.error(f"STDERR:\n{result.stderr}")

        base = os.path.splitext(os.path.basename(circuitFile))[0]
        resultFilePath = os.path.join(self.config.resultDir, f"{base}_result.naviz")
        if not os.path.exists(resultFilePath):
            self.logger.warning(f"ZAC result file not found: {resultFilePath}")
            return None
        return resultFilePath


class NALACCompiler(_QMapBaseCompiler):
    def compileCircuit(self, circuitFile: str):
        arch = json.loads(self.config.archJson)
        archParams = arch.get("architecture", {})
        hardwareSpec = arch.get("hardware_spec", {})
        durationSpec = arch.get("duration_spec", {})
        fidelitySpec = arch.get("fidelity_spec", {})

        cmd = [
            self.config.pythonExecutable,
            os.path.join(self.config.path, "run.py"),
            "--circuit", circuitFile,
            "--result-dir", self.config.resultDir,
            "--array-width", str(archParams.get("array_width")),
            "--array-height", str(archParams.get("array_height")),
            "--aod-columns", str(archParams.get("aod_columns")),
            "--aod-rows", str(archParams.get("aod_rows")),
            "--slm-site-separation", str(hardwareSpec.get("slm_site_separation")),
            "--aod-site-separation", str(hardwareSpec.get("aod_site_separation")),
            "--rydberg-gate-duration", str(durationSpec.get("rydberg_gate_duration")),
            "--single-qubit-gate-duration", str(durationSpec.get("single_qubit_gate_duration")),
            "--atom-transfer-duration", str(durationSpec.get("atom_transfer_duration")),
            "--rydberg-gate-fidelity", str(fidelitySpec.get("rydberg_gate_fidelity")),
            "--single-qubit-gate-fidelity", str(fidelitySpec.get("single_qubit_gate_fidelity")),
            "--atom-transfer-fidelity", str(fidelitySpec.get("atom_transfer_fidelity")),
            "--qubit-coherence-time", str(fidelitySpec.get("T2")),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.stdout:
            self.logger.info(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            self.logger.error(f"STDERR:\n{result.stderr}")

        base = os.path.splitext(os.path.basename(circuitFile))[0]
        resultFilePath = os.path.join(self.config.resultDir, f"{base}_result.naviz")
        if not os.path.exists(resultFilePath):
            self.logger.warning(f"NALAC result file not found: {resultFilePath}")
            return None
        return resultFilePath


class WeaverCompiler(CompilerInterface):
    def compileCircuit(self, circuitFile: str):
        arch = json.loads(self.config.archJson)
        fidelitySpec = arch.get("fidelity_spec", {})
        durationSpec = arch.get("duration_spec", {})
        hardwareSpec = arch.get("hardware_spec", {})
        toleranceSpec = arch.get("tolerance_spec", {})

        cmd = [
            self.config.pythonExecutable,
            os.path.join(self.config.path, "run.py"),
            "--circuit", circuitFile,
            "--result-dir", self.config.resultDir,
            "--u3-gate-fidelity", str(fidelitySpec.get("single_qubit_gate_fidelity")),
            "--cz-gate-fidelity", str(fidelitySpec.get("rydberg_gate_fidelity")),
            "--ccz-gate-fidelity", str(fidelitySpec.get("rydberg_gate_fidelity")),
            "--u3-gate-duration", str(durationSpec.get("single_qubit_gate_duration")),
            "--cz-gate-duration", str(durationSpec.get("rydberg_gate_duration")),
            "--ccz-gate-duration", str(durationSpec.get("rydberg_gate_duration")),
            "--qubit-decay", str(fidelitySpec.get("T1")),
            "--qubit-dephasing", str(fidelitySpec.get("T2")),
            "--shuttling-fidelity", str(fidelitySpec.get("shuttling_fidelity")),
            "--shuttling-speed", str(durationSpec.get("shuttling_speed")),
            "--trap-swap-duration", str(durationSpec.get("atom_transfer_duration")),
            "--trap-swap-fidelity", str(fidelitySpec.get("atom_transfer_fidelity")),
            "--interaction-radius", str(hardwareSpec.get("rydberg_interaction_range")),
            "--restriction-radius", str(hardwareSpec.get("rydberg_interaction_range") * hardwareSpec.get("blockade_radius_factor")),
            "--trap-transfer-proximity", str(toleranceSpec.get("trap_transfer_proximity")),
            "--aod-beam-proximity", str(toleranceSpec.get("aod_beam_proximity")),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.stdout:
            self.logger.info(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            self.logger.error(f"STDERR:\n{result.stderr}")

        resultFilePath = self.getResultFilePath(circuitFile)
        if not os.path.exists(resultFilePath):
            fallbackPath = os.path.join(self.config.resultDir, os.path.basename(circuitFile))
            if os.path.exists(fallbackPath):
                return fallbackPath
            self.logger.warning(f"Weaver result file not found: {resultFilePath}")
            return None
        return resultFilePath

    def getResultFilePath(self, circuitFile: str) -> str:
        base = os.path.splitext(os.path.basename(circuitFile))[0]
        return os.path.join(self.config.resultDir, f"{base}_result.txt")

    def _parseInstructions(self, resultFilePath: str) -> List[str]:
        instructions: List[str] = []
        with open(resultFilePath, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    instructions.append(stripped)
        return instructions

    def _countQubits(self, instructions: List[str]) -> int:
        qDeclPattern = re.compile(r"^qubit\[(\d+)\]\s+q\s*;")
        for line in instructions:
            m = qDeclPattern.match(line)
            if m:
                return int(m.group(1))
        return 0

    def _countMoveOps(self, instructions: List[str]) -> int:
        return sum(1 for line in instructions if line.startswith("@shuttle "))

    def _sumMovingDistance(self, instructions: List[str]) -> float:
        shuttlePattern = re.compile(r"^@shuttle\s+(?:row|col)\s+\d+\s+([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)$")
        total = 0.0
        for line in instructions:
            m = shuttlePattern.match(line)
            if m:
                total += abs(float(m.group(1)))
        return total

    def _countTrapSwaps(self, instructions: List[str]) -> int:
        return sum(1 for line in instructions if line.startswith("@transfer "))

    def _countRydbergActivations(self, instructions: List[str]) -> int:
        return sum(1 for line in instructions if line == "@rydberg")

    def _countRydbergGates(self, instructions: List[str]) -> tuple[int, int]:
        czCount = 0
        cczCount = 0
        inRydbergBlock = False
        for line in instructions:
            if line == "@rydberg":
                inRydbergBlock = True
                continue
            if not inRydbergBlock:
                continue
            if line.startswith("}"):
                inRydbergBlock = False
                continue
            if "ctrl(2) @ U(" in line:
                cczCount += 1
            elif "ctrl @ U(" in line:
                czCount += 1
        return czCount, cczCount

    def _countRamanEventsAndU3Gates(self, instructions: List[str]) -> tuple[int, int]:
        numQubits = self._countQubits(instructions)
        localEvents = 0
        globalEvents = 0
        for line in instructions:
            if line.startswith("@raman local"):
                localEvents += 1
            elif line.startswith("@raman global"):
                globalEvents += 1
        return localEvents + globalEvents, localEvents + (globalEvents * numQubits)

    def _calcFidelity(self, instructions: List[str]) -> float:
        arch = json.loads(self.config.archJson)
        fidelitySpec = arch.get("fidelity_spec", {})
        singleQubitFidelity = fidelitySpec.get("single_qubit_gate_fidelity", 1.0)
        rydbergFidelity = fidelitySpec.get("rydberg_gate_fidelity", 1.0)
        shuttlingFidelity = fidelitySpec.get("shuttling_fidelity", 1.0)
        trapSwapFidelity = fidelitySpec.get("atom_transfer_fidelity", 1.0)

        _, u3GateCount = self._countRamanEventsAndU3Gates(instructions)
        czCount, cczCount = self._countRydbergGates(instructions)
        moveCount = self._countMoveOps(instructions)
        trapSwapCount = self._countTrapSwaps(instructions)

        return (
            (singleQubitFidelity ** u3GateCount)
            * (rydbergFidelity ** (czCount + cczCount))
            * (shuttlingFidelity ** moveCount)
            * (trapSwapFidelity ** trapSwapCount)
        )

    def extractMetrics(self, resultFilePath: str) -> Dict:
        instructions = self._parseInstructions(resultFilePath)
        return {
            "move_count": self._countMoveOps(instructions),
            "total_move_dist": self._sumMovingDistance(instructions),
            "trap_swap_count": self._countTrapSwaps(instructions),
            "num_rydberg_activations": self._countRydbergActivations(instructions),
            "fidelity": self._calcFidelity(instructions),
        }