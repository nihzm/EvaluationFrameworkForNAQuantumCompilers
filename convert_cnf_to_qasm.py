"""One-time CNF to QASM conversion utility for MAX-3SAT benchmarks."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import subprocess
import sys

basisGates = ["u3", "cz"]
_reexecGuardEnvVar = "BACHELORPROJECT_CNF2QASM_REEXEC"


def _maybeReexecWithWeaverPython() -> None:
    """Re-run this script with Weaver's venv Python if available.

    This avoids broken global environments that mix Qiskit <1.0 and >=1.0.
    """
    repoRoot = Path(__file__).resolve().parent
    weaverVenv = repoRoot / "compilers" / "Weaver" / "venv"
    weaverPython = weaverVenv / "bin" / "python"

    if not weaverPython.exists():
        return

    currentPrefix = Path(sys.prefix).resolve()
    if currentPrefix == weaverVenv.resolve():
        return

    # If a stale guard variable is present in the parent shell, still re-exec once
    # as long as we are not already running inside Weaver's venv.
    if os.environ.get(_reexecGuardEnvVar) == "1":
        os.environ.pop(_reexecGuardEnvVar, None)

    env = os.environ.copy()
    env[_reexecGuardEnvVar] = "1"
    cmd = [str(weaverPython), str(Path(__file__).resolve()), *sys.argv[1:]]
    completed = subprocess.run(cmd, env=env, check=False)
    raise SystemExit(completed.returncode)


def _importConversionDependencies():
    """Import heavy conversion dependencies lazily."""
    import numpy as np
    from qiskit import transpile
    from compilers.Weaver.compilers.weaver.utils.hamiltonians import Max3satHamiltonian
    from compilers.Weaver.compilers.weaver.utils.qaoa import QAOA

    return np, transpile, Max3satHamiltonian, QAOA


def convertFile(cnfPath: Path, outputDir: Path, np, transpile, Max3satHamiltonian, QAOA) -> Path:
    """Convert one CNF file into a transpiled QASM file."""
    outputDir.mkdir(parents=True, exist_ok=True)
    outputPath = outputDir / (cnfPath.stem + ".qasm")

    if outputPath.exists():
        return outputPath

    hamiltonian = Max3satHamiltonian(str(cnfPath))
    qaoaSolver = QAOA(hamiltonian)
    qaoaCircuit, costParams, mixerParams = qaoaSolver.naive_qaoa_circuit(1)

    boundCircuit = qaoaCircuit.assign_parameters(
        {
            costParams: [np.pi / 2.123 for _ in costParams],
            mixerParams: [np.pi / 3.123 for _ in mixerParams],
        }
    )
    boundCircuit.measure_all()

    transpiledCircuit = transpile(
        boundCircuit,
        basis_gates=basisGates,
        optimization_level=3,
    )

    outputPath.write_text(transpiledCircuit.qasm(), encoding="utf-8")
    return outputPath


def __extractClauseCountFromFileName(cnfPath: Path) -> int | None:
    """Extract clause count from names like uf20-0200.cnf or uuf100-075.cnf."""
    match = re.search(r"-(\d+)\.cnf$", cnfPath.name, flags=re.IGNORECASE)
    if not match:
        return None
    return int(match.group(1))


def main() -> None:
    """CLI entry point."""
    _maybeReexecWithWeaverPython()

    parser = argparse.ArgumentParser(description="Convert all CNF files in a directory tree to QASM.")
    parser.add_argument(
        "--input-dir",
        dest="inputDir",
        required=True,
        type=Path,
        help="Directory with .cnf files",
    )
    parser.add_argument(
        "--output-dir",
        dest="outputDir",
        required=True,
        type=Path,
        help="Directory for generated .qasm files",
    )
    parser.add_argument(
        "--max-clauses",
        dest="maxClauses",
        type=int,
        default=200,
        help="Only convert CNF files with clause count <= this value (default: 200)",
    )
    args = parser.parse_args()

    np, transpile, Max3satHamiltonian, QAOA = _importConversionDependencies()

    inputDir = args.inputDir.resolve()
    outputDir = args.outputDir.resolve()

    if not inputDir.exists() or not inputDir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {inputDir}")

    allCnfFiles = sorted(pathItem for pathItem in inputDir.rglob("*.cnf") if pathItem.is_file())
    cnfFiles = [
        pathItem
        for pathItem in allCnfFiles
        if (clauseCount := __extractClauseCountFromFileName(pathItem)) is not None
        and clauseCount <= args.maxClauses
    ]

    if not cnfFiles:
        print(f"No CNF files with clauses <= {args.maxClauses} found in {inputDir}")
        return

    print(
        f"Found {len(allCnfFiles)} CNF files total; converting {len(cnfFiles)} "
        f"with clauses <= {args.maxClauses}."
    )

    convertedCount = 0
    for index, cnfFile in enumerate(cnfFiles, start=1):
        outputFile = convertFile(cnfFile, outputDir, np, transpile, Max3satHamiltonian, QAOA)
        convertedCount += 1
        print(f"[{index}/{len(cnfFiles)}] {cnfFile.name} -> {outputFile.name}")

    print(f"Done. Processed {convertedCount} file(s). Output: {outputDir}")


if __name__ == "__main__":
    main()
