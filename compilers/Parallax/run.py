import argparse
import os
import pickle
from typing import Dict
from graphine import graphine
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

    error, success = compile(args.circuit, args.result_dir, args.array_width, args.array_height, args.aod_columns, args.aod_rows, args.radius)
    if success:
        print("Compilation successful.")
    else:
        print(f"Compilation failed with error: {error}")


def compile(circuitPath: str, resultDir: str, array_width: int, array_height: int, aod_columns: int, aod_rows: int, radius: float) -> Dict:

    try:

        # Verify benchmark circuit exists
        if not os.path.exists(circuitPath):
            return (f"Circuit file not found: {circuitPath}", False)
        with open(circuitPath, 'r') as f:
            circuit = f.read()

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

        """
        na.compile_circuit will return the following outputs:
        0 - list of layers of gates 
        1 - number of moves made
        2 - sequential AOD distance moved (used for time for AOD movement; does not include distance from swap traps(see below))
        3 - CZ gate count, 
        4 - U3 gate count 
        5 - number of swap traps = Number of times where qubits needed to change from SLM to AOD to execute a CZ
        6 - distance traveled during swap traps
        7 - list of CZ gates that needed swap traps
        """
        start_c = time.time()
        _, _, _, _, _, _, _, _, fullInstructionList = na.compile_circuit() #TODO make pretiier, only return instruction list
        end_c = time.time()

        base = os.path.splitext(os.path.basename(circuitPath))[0]
        resultPath = os.path.join(resultDir, f"{base}_result.txt")
        os.makedirs(resultDir, exist_ok=True)
        with open(resultPath, 'w') as f:
            for instruction in fullInstructionList:
                f.write(f"{instruction}\n")

        return {'error': None, 'success': True}

    except Exception as e:
        traceback.print_exc(file=sys.stderr)
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
    numQubits = None
    connectCount = {}

    for row in qasmStr.splitlines():
        if 'qreg' in row:
            numQubits = int(row.split('[')[1].split(']')[0])
        if 'measure' in row or 'barrier' in row:
            continue

        qubitMatches = re.findall(r"q\[(\d+)\]", row)
        if len(qubitMatches) > 1:
            qubits = sorted(int(m) for m in qubitMatches)
            for i1 in range(len(qubits) - 1):
                for i2 in range(i1 + 1, len(qubits)):
                    pair = (qubits[i1], qubits[i2])
                    connectCount[pair] = connectCount.get(pair, 0) + 1

    if numQubits is None:
        raise ValueError("Could not determine number of qubits from QASM file")

    return numQubits, connectCount


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