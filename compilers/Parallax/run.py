import argparse
import os
import pickle
from typing import Dict, List
from na_arch import NA_Architecture
import time
import sys
import json
import traceback


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--circuit', required=True, help='Path to circuit file')
    parser.add_argument('--result-dir', default='results', help='Output directory')
    parser.add_argument('--array-width', type=int,help='Width of the qubit array')
    parser.add_argument('--array-height', type=int, help='Height of the qubit array')
    parser.add_argument('--aod-columns', type=int, help='Number of columns in the AOD')
    parser.add_argument('--aod-rows', type=int, help='Number of rows in the AOD')
    parser.add_argument('--radius', type=float, help='Rydberg radius (in units of grid spacing)')
    args = parser.parse_args()

    result = compile(args.circuit, args.result_dir, args.array_width, args.array_height, args.aod_columns, args.aod_rows, args.radius)
    if result['success']:
        print("Compilation successful.")
    else:
        print(f"Compilation failed with error: {result['error']}")

def compile(circuitPath: str, resultDir: str, array_width: int, array_height: int, aod_columns: int, aod_rows: int, radius: float) -> Dict:

    try:

        # Verify benchmark circuit exists
        if not os.path.exists(circuitPath):
            return (f"Circuit file not found: {circuitPath}", False)
        with open(circuitPath, 'r') as f:
            circuit = f.read()

        # Normalize to a QASM2 form that Parallax internals can parse reliably.
        circuit = _normalizeQasmForParallax(circuit)

        # Parse QASM to extract qubit count and gate connectivity
        numQubits, connectCount = _parseQasmConnectivity(circuit)

        # Place qubits on a simple square grid
        qubitPositions = _placeOnSquareGrid(numQubits, array_width, array_height)

        # Map qubit positions to discrete integer grid and adjust Rydberg radius accordingly
        mappedPoints, adjustedRadius = _mapToBoundedInteger(qubitPositions, array_width, array_height, radius)

        """
        The args for the NA_Architecture object are:
        0 - [number_AOD_rows, number_AOD_cols] - The size of the AOD
        1 - [atoms_in_x_axis, atoms_in_y_axis] - The number of atoms in the computer (ex: 35x35 for the Atom computer)
        2 - Discretized coordinate list for the qubits involved in the circuit
        3 - List of counts of gates between qubits
        4 - Rydberg Radius
        5 - qasm string that represents the input circuit 
        """
        na = NA_Architecture([aod_rows, aod_columns], [array_width, array_height], mappedPoints, connectCount, adjustedRadius, circuit)

        fullInstructionList = na.compile_circuit()

        base = os.path.splitext(os.path.basename(circuitPath))[0]
        resultPath = os.path.join(resultDir, f"{base}_result.txt")
        os.makedirs(resultDir, exist_ok=True)
        with open(resultPath, 'w') as f:
            for instruction in fullInstructionList:
                f.write(f"{instruction}\n")

        return {'error': None, 'success': True}

    except Exception as e:
        return {'error': str(e), 'success': False} 
    

def _mapToBoundedInteger(points, width, height, radius):
    # Initialize a set to keep track of filled locations
    filledLocations = set()
    # Initialize a list to hold points that couldn't be placed immediately
    holdList = []
    # Initialize the list of mapped points
    mappedPoints = []

    # Function to find the closest empty discrete location
    def __findClosestEmpty(x, y):
        # Check all possible locations in increasing distance
        for dx in range(max(width, height)):
            for dy in range(max(width, height)):
                # Check in all four directions
                for nx, ny in [(x+dx, y+dy), (x+dx, y-dy), (x-dx, y+dy), (x-dx, y-dy)]:
                    if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in filledLocations:
                        return nx, ny
        # If no empty location is found
        return None

    # Attempt to map each point
    for (x, y) in points:
        mappedX = int(x * width)
        mappedY = int(y * height)
        # If the location is already filled, add the point to the hold list
        if (mappedX, mappedY) in filledLocations:
            holdList.append((x, y))
        else:
            # Place the point and mark the location as filled
            mappedPoints.append((mappedX, mappedY))
            filledLocations.add((mappedX, mappedY))
    # Process points in the hold list
    for (x, y) in holdList:
        closestEmpty = __findClosestEmpty(int(x * width), int(y * height))
        if closestEmpty is None:
            # If there are no empty locations left, raise an exception
            raise Exception("Not enough room in SLM for all qubits to be loaded.")
        else:
            # Place the point from the hold list to the closest empty location
            mappedPoints.append(closestEmpty)
            filledLocations.add(closestEmpty)

    # Expand Rydberg radius proportionally to longer of the two dimensions
    radius = radius * max(width, height)
    return mappedPoints, radius


def _parseQasmConnectivity(qasmStr: str):
    """
    Parse a QASM string to extract the number of qubits and gate connectivity counts.
    Returns (numQubits, connectCount) where connectCount is a dict {(q1,q2): count}.
    """
    import re
    numQubits = 0
    connectCount = {}

    # Track declared quantum registers and build global qubit ids.
    # Example: qreg q[5]; qreg anc[2]; => offsets {"q":0, "anc":5}
    regOffsets = {}

    for row in qasmStr.splitlines():
        stripped = row.strip()
        if not stripped or stripped.startswith('//'):
            continue

        qregMatch = re.match(r"^qreg\s+([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\]\s*;", stripped)
        if qregMatch:
            regName = qregMatch.group(1)
            regSize = int(qregMatch.group(2))
            if regName not in regOffsets:
                regOffsets[regName] = numQubits
                numQubits += regSize
            continue

        qasm3QubitMatch = re.match(r"^qubit\s*\[(\d+)\]\s*([A-Za-z_][A-Za-z0-9_]*)\s*;", stripped)
        if qasm3QubitMatch:
            regSize = int(qasm3QubitMatch.group(1))
            regName = qasm3QubitMatch.group(2)
            if regName not in regOffsets:
                regOffsets[regName] = numQubits
                numQubits += regSize
            continue

        if 'measure' in row or 'barrier' in row:
            continue

        # Find all register[index] uses and keep only known quantum registers.
        qubitMatches = re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\]", row)
        gateQubits: List[int] = []
        for regName, idxStr in qubitMatches:
            if regName not in regOffsets:
                continue
            gateQubits.append(regOffsets[regName] + int(idxStr))

        if len(gateQubits) > 1:
            qubits = sorted(gateQubits)
            for i1 in range(len(qubits) - 1):
                for i2 in range(i1 + 1, len(qubits)):
                    pair = (qubits[i1], qubits[i2])
                    connectCount[pair] = connectCount.get(pair, 0) + 1

    if numQubits == 0:
        raise ValueError("Could not determine number of qubits from QASM file")

    return numQubits, connectCount


def _normalizeQasmForParallax(qasmStr: str) -> str:
    """
    Normalize OpenQASM input for Parallax internals:
    - Accept OpenQASM 2 and 3
    - Remove non-unitary operations (e.g., measure/barrier)
    - Transpile to a compact Parallax-friendly basis (u3, cz)
    - Emit OpenQASM 2
    """
    import re

    try:
        from qiskit import QuantumCircuit, qasm2, qasm3, transpile

        # Parse either OpenQASM 2 or OpenQASM 3.
        if re.search(r"OPENQASM\s+3", qasmStr, flags=re.IGNORECASE):
            qc = qasm3.loads(qasmStr)
        else:
            qc = qasm2.loads(qasmStr)

        # Remove final measurements (and associated classical bits, where possible).
        qc = qc.remove_final_measurements(inplace=False)

        # Drop non-unitary / classically driven operations that Parallax does not execute.
        clean_qc = QuantumCircuit(*qc.qregs, name=qc.name)
        clean_qc.global_phase = qc.global_phase
        for inst, qargs, cargs in qc.data:
            if inst.name in {"measure", "barrier", "reset", "delay"}:
                continue
            if cargs:
                continue
            clean_qc.append(inst, qargs, [])

        # Normalize gate set for downstream Parallax parsing/execution model.
        norm_qc = transpile(clean_qc, basis_gates=["u3", "cz"], optimization_level=2)
        qasm2_str = qasm2.dumps(norm_qc)

        return qasm2_str
    except Exception as e:
        raise ValueError(f"Failed to normalize QASM for Parallax: {e}") from e


def _placeOnSquareGrid(numQubits: int, width: int, height: int):
    """
    Place qubits on a simple square grid layout, row by row.
    Returns a list of (x, y) integer coordinate tuples.
    """
    import math
    cols = math.ceil(math.sqrt(numQubits))
    positions = []
    for i in range(numQubits):
        x = i % cols
        y = i // cols
        if x >= width or y >= height:
            raise ValueError(f"Not enough room on {width}x{height} grid for {numQubits} qubits")
        positions.append((x, y))
    return positions


if __name__ == "__main__":
    raise SystemExit(main())