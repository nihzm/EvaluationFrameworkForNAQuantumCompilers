"""
Main entry point for Benchmark Tool
"""

import sys
from benchmark import BenchmarkManager
from cli import listCompilers, parseArguments
from configClasses import BenchmarkConfig


def main():
    """
    Main entry point
    """

    args = parseArguments()

    # If --list-compilers flag is set, display available compilers and exit
    if args.list_compilers:
        listCompilers()
        return

    # Create benchmark configuration
    config = BenchmarkConfig(
        compilers=args.compilers,
        benchmarkSets=args.benchmark_sets,
        outputDir=args.output,
        numRuns=args.num_runs,
        timeout=args.timeout,
        arch=args.arch
    )

    # Create and (try to) initialize benchmark manager - exit on failure
    manager = BenchmarkManager(config)
    if not manager.initializeCompilers():
        for compiler in config.compilers:
            if compiler not in manager.compilers:
                print(f"Error: Compiler '{compiler}' failed to initialize.")
        return 1

    # Running the compilers on the benchmarks
    try:

        # Execute the whole benchmarking process
        manager.runBenchmarks()

        # TODO: pretty print or overview over succesfull runs / failed runs etc.

        return 0

    except KeyboardInterrupt:
        print("\nBenchmark interrupted by user.")
        return 130
    
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
