from pysat.formula import CNF
from compilers.weaver.compiler.entrypoint import Max3satQaoaCompiler
from compilers.weaver.nac.config import FPQAConfig
#from utils.hamiltonians import Max3satHamiltonian
#from utils.qaoa import QAOA
#from qiskit import transpile
import os
import pdb
import time
import pandas as pd
from compilers.weaver.utils.sat_utils import get_color_map

data = []
columns = [
    "name", 
    "num_variables", 
    "num_clauses", 
    "num_colors", 
    "compilation_time (seconds)", 
    "execution_time (microseconds)",
    "eps (fidelity)", 
    "#u3", 
    "#cz",
    "#ccz", 
    "ccz_fidelity", 
    "fpqa_config"
]

def run():

    # -- Adding a check if results file already exists ----------------------------------------------
    #results_path = "results/weaver_results.csv"
    #if os.path.exists(results_path) and os.path.getsize(results_path) > 0:
    #    print(f"Skipping: '{results_path}' already exists and is non-empty.")
    #   return
    # -----------------------------------------------------------------------------------------------

    ccz_fidelities = [0.9775, 0.98, 0.9825, 0.985, 0.9875, 0.99, 0.9925, 0.995, 0.9975]
    benchmarks = list(filter(lambda f: f.endswith(".cnf"), os.listdir("./benchmarks/max3SAT")))
    num_benchmarks = len(benchmarks)

    for index, filename in enumerate(benchmarks):

        fpqa_config = FPQAConfig({}) # Prepares the FPQA configuration with default parameters in /compilers/weaver/nac/config.py for gate fidelities, durations, qubit decoherence times, shuttling speeds, etc.
        
        print(f"Compiling {filename} ({index + 1}/{num_benchmarks})...")
        if not filename.endswith(".cnf"):
            continue

        formula = CNF(from_file=f"./benchmarks/max3SAT/{filename}") # load the formula from the top of the cnf file
        num_colors, color_map = get_color_map(formula) # graph coloring of the clause-interaction graph of a CNF formula — specifically using DSATUR-style greedy coloring

        start_time = time.time()

        compiler = Max3satQaoaCompiler(formula, fpqa_config) # weaver entrypoint/compiler, create compiler instance with formula and config

        # -- Compile the program -> returns an FPQAProgram instance ------------------------------------------------
        program = compiler.compile_single_layer() # Assumptions: One aod row, triangular slm layout, single-layer QAOA

        # -- Added: Printing the FPQA Program of the last compiled instance -----------------------------------------
        results_dir = "wQasm_result"
        os.makedirs(results_dir, exist_ok=True)

        result_filename = filename.replace(".cnf", "_result.txt")
        result_path = os.path.join(results_dir, result_filename)

        if os.path.exists(result_path):
            print(f"Skipping write: {result_path} already exists.")
        else:
            with open(result_path, "w") as f:
                f.write(program.to_string())
        # ------------------------------------------------------------------------------------------------------------

        # -- Collecting statistics for different CCZ fidelities and storing them in a CSV table --------------------
        execution_time = program.duration()
        gates = program.count_ops()
        end_time = time.time()
        compilation_time = end_time - start_time
        for ccz_fidelity in ccz_fidelities:
            program.fpqa.config.CCZ_GATE_FIDELITY = ccz_fidelity
            fidelity = program.avg_fidelity()
            row = [
                filename, 
                str(formula.nv), 
                str(len(formula.clauses)), 
                str(num_colors), 
                str(compilation_time), 
                str(execution_time), 
                str(fidelity), 
                str(gates["u3"]), 
                str(gates["cz"]), 
                str(gates["ccz"]), 
                str(ccz_fidelity), 
                fpqa_config.to_string()
            ]
            data.append(row)

    df = pd.DataFrame(data, columns=columns)
    df.to_csv("results/weaver_results.csv")