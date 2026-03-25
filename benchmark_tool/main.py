"""
Main entry point for Benchmark Tool
"""

import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from benchmark import BenchmarkManager
from cli import listCompilers, parseArguments
from configClasses import BenchmarkConfig
from registry import COMPILER_REGISTRY, PARAMETER_CATALOG

def main():
    """
    Main entry point
    """

    args = parseArguments()

    # If --list-compilers flag is set, display available compilers and exit
    if args.list_compilers:
        listCompilers()
        return
    
    # Build architecture configuration based on selected compilers and user input
    try:
        arch = _buildArchitectureConfig(args.compilers)
    except Exception as e:
        print(f"Error building architecture configuration: {e}")
        return 1

    # Create benchmark configuration
    config = BenchmarkConfig(
        compilers=args.compilers,
        benchmarkSet=args.benchmark_set,
        outputDir=args.output,
        numRuns=args.num_runs,
        timeout=args.timeout,
        arch=arch,
        cnf=args.cnf,
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


def _buildArchitectureConfig(args_compilers: list[str]) -> Path:
    """
    Create an architecture JSON file for the selected compilers.

    Uses:
      - COMPILER_REGISTRY
      - PARAMETER_CATALOG
      - architectures/default_arch.json

    Behavior:
      1) Load defaults from architectures/default_arch.json
      2) Ask whether defaults should be used or configuration should be customized
      3) Compute the union of required parameters across selected compilers
      4) If customizing, prompt once per parameter and allow Enter to keep default
      5) Save as architectures/<timestamp>_arch.json
    """

    # 1. Basic validation of inputs and defaults
    if not args_compilers:
        raise ValueError("args_compilers must not be empty")

    unknown_compilers = [c for c in args_compilers if c not in COMPILER_REGISTRY]
    if unknown_compilers:
        raise ValueError(f"Unknown compilers: {unknown_compilers}")

    if not Path("architectures/default_arch.json").exists():
        raise FileNotFoundError(f"Default architecture file not found: architectures/default_arch.json")

    # 2. Load defaults as fallback values for parameters
    with Path("architectures/default_arch.json").open("r", encoding="utf-8") as f:
        arch_config = json.load(f)

    # 3. Compute required parameters for selected compilers
    required_parameter_keys: set[str] = set()
    for compiler_name in args_compilers:
        required_parameter_keys.update(
            COMPILER_REGISTRY[compiler_name].get("required_parameters", [])
        )
    ordered_keys = sorted(required_parameter_keys)

    # 4. Internal consistency check: Ensure all required parameters are in the catalog and have defaults
    missing_catalog_entries = sorted(key for key in ordered_keys if key not in PARAMETER_CATALOG)
    if missing_catalog_entries:
        raise ValueError(
            "Missing PARAMETER_CATALOG entries for: "
            f"{missing_catalog_entries}"
        )
    missing_defaults = sorted(key for key in ordered_keys if not __hasNested(arch_config, key))
    if missing_defaults:
        raise ValueError(
            "The default architecture JSON is missing required parameters: "
            f"{missing_defaults}"
        )


    # 5. Prompt user to use defaults or customize
    while True:
        choice = input(
            "\nUse defaults from architectures/default_arch.json or customize the configuration?\n"
            "  [D]efaults / [C]ustomize: "
        ).strip().lower()

        if choice in {"d", "default", "defaults"}:
            customize = False
            break
        if choice in {"c", "customize", "configure"}:
            customize = True
            break

        print("Please enter 'd' for defaults or 'c' for customize.")

    # 6. If customizing, prompt for each required parameter with current default shown and allow Enter to keep default
    if customize:
        total = len(ordered_keys)
        for index, key in enumerate(ordered_keys, start=1):
            spec = PARAMETER_CATALOG[key]
            expected_type = spec.get("type", str)
            prompt = spec.get("prompt", key)
            description = spec.get("description", "")

            current_default = __getNested(arch_config, key)

            print()
            print(f"• ({index}/{total}) Configuring '{prompt}': {description}")
            print(f"  Default value: {__formatDefault(current_default)} (Press Enter to use default)")
            print("  " + "-" * 70)

            while True:
                raw = input("  Enter value: ").strip()

                if raw == "":
                    break

                try:
                    value = __coerceParameterValue(raw, expected_type)
                    __setNested(arch_config, key, value)
                    break
                except ValueError as exc:
                    print(f"  Invalid value: {exc}")

    # 7. Save the resulting architecture configuration to a new JSON file with timestamped name in architectures/ and return the path to the new file
    output_dir = Path("architectures")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"{timestamp}_arch.json"

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(arch_config, f, indent=2)

    print(f"\nSaved architecture config to: {output_path}")
    return output_path


def __setNested(config: dict[str, Any], dotted_key: str, value: Any) -> None:
    parts = dotted_key.split(".")
    current = config
    for part in parts[:-1]:
        current = current.setdefault(part, {})
    current[parts[-1]] = value


def __getNested(config: dict[str, Any], dotted_key: str) -> Any:
    parts = dotted_key.split(".")
    current = config
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            raise KeyError(dotted_key)
        current = current[part]
    return current


def __hasNested(config: dict[str, Any], dotted_key: str) -> bool:
    try:
        __getNested(config, dotted_key)
        return True
    except KeyError:
        return False


def __coerceParameterValue(raw: str, expected_type: type) -> Any:
    raw = raw.strip()

    if expected_type is bool:
        lowered = raw.lower()
        if lowered in {"true", "t", "yes", "y", "1"}:
            return True
        if lowered in {"false", "f", "no", "n", "0"}:
            return False
        raise ValueError("Please enter true/false, yes/no, or 1/0.")

    if expected_type is int:
        return int(raw)

    if expected_type is float:
        return float(raw)

    return raw


def __formatDefault(default: Any) -> str:
    if isinstance(default, bool):
        return "true" if default else "false"
    return str(default)




if __name__ == "__main__":
    sys.exit(main())
