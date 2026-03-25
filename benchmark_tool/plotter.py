from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt


def _latest_metrics_dir(metrics_root: Path) -> Path:
    candidates = [p for p in metrics_root.iterdir() if p.is_dir()]
    if not candidates:
        raise FileNotFoundError(f"No metrics folders found in {metrics_root}")
    return sorted(candidates)[-1]


def _load_json(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _qubits_from_name(path: Path) -> Optional[int]:
    # Expected benchmark naming, e.g. dj_indep_opt0_10.qasm or 4gt4-v0_80.qasm
    m = re.search(r"_(\d+)\.qasm$", path.name)
    if m:
        return int(m.group(1))
    return None


def _build_qubit_index(benchmarks_root: Path) -> Dict[str, int]:
    """Build lookup: benchmark path/name/stem -> qubit count, excluding benchmarks/test."""
    index: Dict[str, int] = {}
    if not benchmarks_root.exists():
        return index

    for qasm_file in benchmarks_root.rglob("*.qasm"):
        if any(part.lower() == "test" for part in qasm_file.parts):
            continue

        q = _qubits_from_name(qasm_file)
        if q is None:
            continue

        abs_key = str(qasm_file.resolve())
        rel_key = str(qasm_file)
        name_key = qasm_file.name
        stem_key = qasm_file.stem

        index[abs_key] = q
        index[rel_key] = q
        index[name_key] = q
        index[stem_key] = q

    for cnf_file in benchmarks_root.rglob("*.cnf"):
        if any(part.lower() == "test" for part in cnf_file.parts):
            continue

        q = _qubits_from_name(cnf_file)
        if q is None:
            continue

        abs_key = str(cnf_file.resolve())
        rel_key = str(cnf_file)
        name_key = cnf_file.name
        stem_key = cnf_file.stem

        index[abs_key] = q
        index[rel_key] = q
        index[name_key] = q
        index[stem_key] = q

    return index


def _resolve_qubit_count(benchmark_path: str, qubit_index: Dict[str, int]) -> Optional[int]:
    p = Path(benchmark_path)
    abs_key = str(p.resolve()) if p.exists() else str(p)

    # Try path-based lookup first
    if abs_key in qubit_index:
        return qubit_index[abs_key]
    if benchmark_path in qubit_index:
        return qubit_index[benchmark_path]

    # Fallback by filename/stem
    if p.name in qubit_index:
        return qubit_index[p.name]
    if p.stem in qubit_index:
        return qubit_index[p.stem]

    return _qubits_from_name(p)


def _metric_series(
    payload: Dict,
    run_id: str,
    qubit_index: Dict[str, int],
    metric_keys: List[str],
) -> Tuple[List[int], List[float]]:
    benchmarks = payload.get("benchmarks", [])
    runs = payload.get("runs", {})
    run = runs.get(run_id)
    if run is None:
        # fallback to first available run
        if not runs:
            return [], []
        first_key = sorted(runs.keys())[0]
        run = runs[first_key]

    # Support alternative names to be robust across compiler implementations.
    y_vals = None
    for key in metric_keys:
        if run.get(key) is not None:
            y_vals = run.get(key)
            break

    if y_vals is None:
        return [], []

    points: List[Tuple[int, float]] = []
    for bench, y in zip(benchmarks, y_vals):
        q = _resolve_qubit_count(bench, qubit_index)
        if q is None or y is None:
            continue
        points.append((q, float(y)))

    points.sort(key=lambda t: t[0])
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    return x, y


def _plot_metric_vs_qubits(
    metrics_dir: Path,
    qubit_index: Dict[str, int],
    out_file: Path,
    y_label: str,
    metric_keys: List[str],
    run_id: str = "0",
    show: bool = False,
) -> None:
    compiler_files = sorted(metrics_dir.glob("*.json"))
    if not compiler_files:
        raise FileNotFoundError(f"No compiler metric json files found in {metrics_dir}")

    # Friend-like style: thin lines, tiny circular markers, clean grid.
    plt.figure(figsize=(10, 6))

    style_cycle = [
        {"marker": "o", "linestyle": "-"},
        {"marker": "s", "linestyle": "--"},
        {"marker": "^", "linestyle": "-."},
        {"marker": "D", "linestyle": ":"},
        {"marker": "v", "linestyle": "-"},
        {"marker": "P", "linestyle": "--"},
    ]

    for i, comp_file in enumerate(compiler_files):
        payload = _load_json(comp_file)
        compiler_name = payload.get("compiler", comp_file.stem)
        x, y = _metric_series(payload, run_id, qubit_index, metric_keys)
        if not x:
            continue

        style = style_cycle[i % len(style_cycle)]
        plt.plot(
            x,
            y,
            marker=style["marker"],
            markersize=4,
            linewidth=1.2,
            linestyle=style["linestyle"],
            alpha=0.8,
            markerfacecolor="white",
            markeredgewidth=0.9,
            label=compiler_name.upper(),
        )

    plt.xlabel("Number of qubits")
    plt.ylabel(y_label)
    plt.grid(True, alpha=0.35)
    plt.legend()
    plt.tight_layout()

    out_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close()


def plot_rydberg_vs_qubits(
    metrics_dir: Path,
    qubit_index: Dict[str, int],
    out_file: Path,
    run_id: str = "0",
    show: bool = False,
) -> None:
    _plot_metric_vs_qubits(
        metrics_dir=metrics_dir,
        qubit_index=qubit_index,
        out_file=out_file,
        y_label="Number of Rydberg activations",
        metric_keys=["num_rydberg_activations", "num_layers"],
        run_id=run_id,
        show=show,
    )


def plot_sum_distance_vs_qubits(
    metrics_dir: Path,
    qubit_index: Dict[str, int],
    out_file: Path,
    run_id: str = "0",
    show: bool = False,
) -> None:
    _plot_metric_vs_qubits(
        metrics_dir=metrics_dir,
        qubit_index=qubit_index,
        out_file=out_file,
        y_label="Sum moving distance",
        metric_keys=["total_move_dist"],
        run_id=run_id,
        show=show,
    )


def plot_trap_swap_vs_qubits(
    metrics_dir: Path,
    qubit_index: Dict[str, int],
    out_file: Path,
    run_id: str = "0",
    show: bool = False,
) -> None:
    _plot_metric_vs_qubits(
        metrics_dir=metrics_dir,
        qubit_index=qubit_index,
        out_file=out_file,
        y_label="Trap swap count",
        metric_keys=["trap_swap_count"],
        run_id=run_id,
        show=show,
    )


def plot_fidelity_vs_qubits(
    metrics_dir: Path,
    qubit_index: Dict[str, int],
    out_file: Path,
    run_id: str = "0",
    show: bool = False,
) -> None:
    _plot_metric_vs_qubits(
        metrics_dir=metrics_dir,
        qubit_index=qubit_index,
        out_file=out_file,
        y_label="Fidelity",
        metric_keys=["fidelity"],
        run_id=run_id,
        show=show,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plot one line per compiler for multiple metrics against qubit count"
    )
    parser.add_argument(
        "--metrics-root",
        type=Path,
        default=Path("results/metrics"),
        help="Root folder containing per-architecture metrics subfolders.",
    )
    parser.add_argument(
        "--benchmarks-root",
        type=Path,
        default=Path("benchmarks"),
        help="Benchmark root used to map benchmark names to qubit counts (folder 'test' is ignored).",
    )
    parser.add_argument(
        "--metrics-dir",
        type=Path,
        default=None,
        help="Explicit metrics folder (e.g., results/metrics/<arch>). If omitted, latest folder is used.",
    )
    parser.add_argument(
        "--run-id",
        default="0",
        help="Run id to plot (default: 0). Falls back to first available run if missing.",
    )
    parser.add_argument(
        "--out-rydberg",
        type=Path,
        default=Path("results/plots/rydberg_activations_vs_qubits.png"),
        help="Output path for rydberg activations vs qubits plot.",
    )
    parser.add_argument(
        "--out-distance",
        type=Path,
        default=Path("results/plots/sum_distance_vs_qubits.png"),
        help="Output path for sum distance vs qubits plot.",
    )
    parser.add_argument(
        "--out-trap-swap",
        type=Path,
        default=Path("results/plots/trap_swap_vs_qubits.png"),
        help="Output path for trap swap count vs qubits plot.",
    )
    parser.add_argument(
        "--out-fidelity",
        type=Path,
        default=Path("results/plots/fidelity_vs_qubits.png"),
        help="Output path for fidelity vs qubits plot.",
    )
    parser.add_argument("--show", action="store_true", help="Show figure interactively.")
    args = parser.parse_args()

    metrics_dir = args.metrics_dir if args.metrics_dir is not None else _latest_metrics_dir(args.metrics_root)
    qubit_index = _build_qubit_index(args.benchmarks_root)
    plot_rydberg_vs_qubits(
        metrics_dir=metrics_dir,
        qubit_index=qubit_index,
        out_file=args.out_rydberg,
        run_id=args.run_id,
        show=False,
    )
    plot_sum_distance_vs_qubits(
        metrics_dir=metrics_dir,
        qubit_index=qubit_index,
        out_file=args.out_distance,
        run_id=args.run_id,
        show=False,
    )
    plot_trap_swap_vs_qubits(
        metrics_dir=metrics_dir,
        qubit_index=qubit_index,
        out_file=args.out_trap_swap,
        run_id=args.run_id,
        show=False,
    )
    plot_fidelity_vs_qubits(
        metrics_dir=metrics_dir,
        qubit_index=qubit_index,
        out_file=args.out_fidelity,
        run_id=args.run_id,
        show=args.show,
    )
    print(f"Saved plot to {args.out_rydberg}")
    print(f"Saved plot to {args.out_distance}")
    print(f"Saved plot to {args.out_trap_swap}")
    print(f"Saved plot to {args.out_fidelity}")


if __name__ == "__main__":
    main()