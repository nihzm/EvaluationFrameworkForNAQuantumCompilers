# Weaver

## Overview
This artifact includes Weaver's quantum optimization framework and baseline FPQA compilers, enabling comparisons across execution time, compilation time, and fidelity metrics. The project uses benchmark instances from the SATLIB repository to evaluate the efficiency and performance of different quantum compilers on MAX-3SAT problem instances, with results replicating the figures presented in the accompanying research paper.
This artifact includes Weaver, which features an optimized compilation procedure for neutral atoms based on the MAX-3SAT formulation, along with the following baseline FPQA compilers for comparison:

- Geyser (as described in Patel et al., 2022)
- Atomique (as described in Wang et al., 2024)
- Qiskit (used for a superconducting circuit baseline)
- Weaver achieves significant improvements over baseline methods, with up to a 10^3x faster execution time, 4.4x faster compilation time, and 10% average improvement in fidelity.

## Requirements
To run the benchmarking suite, please ensure you have:

- Python 3.11.2 or higher.
- PDM (Python Dependency Manager) for managing dependencies (steps to install PDM are in the Installation section).

Additional Python packages listed in pyproject.toml:
- PyYAML
- pdbpp
- matplotlib
- qiskit
- (and any other dependencies as specified in the file)

The pyproject.toml file automatically manages these dependencies when using PDM.

## Installation
Set up a virtual environment of your choice (or use the default method below):

1. Inicialize virtual enviroment
`python -m venv .venv`

2. Activate the virtual environment:
`source .venv/bin/activate`

3. Install PDM:
`pip install pdm`

4. Install dependencies:
`pdm install`

This setup will configure the required dependencies within the virtual environment, enabling you to run the artifact scripts smoothly.

To reproduce the results, navigate to the main folder and run:
`python run.py`

## Workflow Overview
Running run.py will execute several scripts sequentially to process MAX-3SAT instances, run the compilers, and produce plots. Below is a summary of each stage, including approximate runtimes:

1. Transpiling MAX-3SAT Instances to Quantum Circuits (Approx. 10 minutes): Converts MAX-3SAT instances into QAOA quantum circuits in QASM format.

2. Running Compilers:

- Atomique (Approx. 30 minutes): Runs Atomique on circuits of sizes 20 to 250 with 10 variants per size.
- Superconducting (Qiskit) (Approx. 20 minutes): Transpiles circuits for sizes up to 100 qubits, using the Qiskit transpiler for the "Washington" backend.
- Geyser (Approx. 7 hours): Compiles 10 circuits of size 20 qubits (longer sizes exceed the 20-hour limit).
- Weaver (Approx. 20 minutes): Runs on all sizes and variants.

3. Converting to DPQA Format (Approx. 10 minutes): Converts QASM circuits to DPQA-compatible JSON format for DPQA processing.

4. Running DPQA (Approx. 10 hours): Runs DPQA on 10 circuits of size 20 (larger benchmarks exceed runtime limits).

5. Plotting Results: Generates the four key figures from the research paper.

- Compilation Time Comparison
- Execution Time Comparison
- Fidelity Comparison
- Analysis Plots (with complexity metrics and CCZ fidelity thresholds)

## Evaluation and Expected Results
The script will output runtime information for each step, providing progress updates and preventing confusion if stages take longer. Variations in output plots compared to the paper should be minimal (not exceeding 5%).