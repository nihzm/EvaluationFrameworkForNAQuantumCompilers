"""
Command Line Interface for Benchmark Tool
"""

import argparse
from pathlib import Path
from registry import COMPILER_REGISTRY


def jsonFilePath(value: str) -> Path:
    """
    Validate that the provided value is a path to a .json file.
    """

    path = Path(value)
    if path.suffix.lower() != ".json":
        raise argparse.ArgumentTypeError("--arch must point to a .json file")
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"--arch file does not exist: {path}")
    return path

def parseArguments():
    """
    Parse command line arguments
    """

    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Benchmark Tool for Neutral Atom Quantum Compilers",    
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Examples:
            # Run all compilers on default benchmarks
            python -m benchmark_tool

            # Run specific compilers
            python -m benchmark_tool --compilers atomique parallax zac

            # Run with custom settings
            python -m benchmark_tool --compilers atomique --num-runs 5 --output results/
            """,
        )

    # Argument: Which compilers to benchmark (Default: all)
    parser.add_argument(
        "--compilers",
        nargs="+",
        choices=list(COMPILER_REGISTRY.keys()),
        default=list(COMPILER_REGISTRY.keys()),
        help="Compilers to benchmark",
    )

    # Argument: Which benchmark sets to run (Default: all)
    parser.add_argument(
        "--benchmark-set",
        type=Path,
        default=Path("benchmarks/qasm/qft_opt0_indep"),
        help="Path to benchmark set directory",
    )

    # Argument: Its a .cnf benchmark set (Default: False)
    parser.add_argument(
        "--cnf",
        action="store_true",
        help="Indicate that the benchmark set is in .cnf format",
    )
    
    # Argument: Output directory for results (Default: ./results)
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("./results"),
        help="Output directory for results",
    )

    # Argument: Number of runs per benchmark (Default: 1)
    parser.add_argument(
        "--num-runs",
        type=int,
        default=1,
        help="Number of runs per benchmark",
    )

    # Argument: Timeout per benchmark (Default: 300 seconds)
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout per benchmark (seconds)",
    )

    # Argument: Outputs list of available compilers
    parser.add_argument(
        "--list-compilers",
        action="store_true",
        help="List all available compilers",
    )

    return parser.parse_args()

def listCompilers():
    """
    Display available compilers
    """
    
    print("\nAvailable Compilers:")
    print("-" * 60)
    for name, info in COMPILER_REGISTRY.items():
        print(f"  {name:15s} - {info['description']}")
    print("-" * 60)