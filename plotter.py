"""Plotter for quantum compiler benchmark metrics."""

from __future__ import annotations

import argparse
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


logger = logging.getLogger(__name__)


class Plotter:
    """Plot metrics from a metrics/<timestamp>_arch folder."""

    def __init__(self, metrics_dir: Optional[Path]):
        """
        Initialize plotter with metrics folder.
        
        Args:
            metrics_dir: Path to metrics/<timestamp>_arch folder
        """
        self.metrics_dir = Path(metrics_dir) if metrics_dir is not None else None
        self.compiler_files: List[Path] = []

        if self.metrics_dir is None:
            return

        if not self.metrics_dir.exists():
            raise FileNotFoundError(f"Metrics folder not found: {self.metrics_dir}")

        self.compiler_files = sorted(self.metrics_dir.glob("*.json"))
        if self.compiler_files:
            logger.info(f"Loaded {len(self.compiler_files)} compiler metric files from {self.metrics_dir}")

    def _extract_metric_values(self, run_data: Dict, y_metric: str) -> Optional[List[float]]:
        """Extract metric values from a run payload for the requested metric."""
        metric_keys = {
            "total_move_dist": ["total_move_dist"],
            "trap_swap_count": ["trap_swap_count"],
            "num_rydberg_activations": ["num_rydberg_activations", "num_layers"],
        }

        if y_metric not in metric_keys:
            raise ValueError(f"Unknown metric: {y_metric}. Must be one of {list(metric_keys.keys())}")

        for key in metric_keys[y_metric]:
            if key in run_data:
                values: List[float] = []
                for v in run_data[key]:
                    if v is None:
                        continue
                    try:
                        values.append(float(v))
                    except (ValueError, TypeError):
                        continue
                return values
        return None

    def _load_json(self, path: Path) -> Dict:
        """Load JSON file."""
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _extract_benchmark_property(
        self, benchmark_name: str, property_type: str
    ) -> Optional[int]:
        """
        Extract a property from benchmark name.
        
        Args:
            benchmark_name: Name like 'uf100-025.cnf' or 'qft_opt0_10.qasm'
            property_type: One of 'variables', 'clauses', or 'aod_rows'
        
        Returns:
            The extracted value, or None if not found
        """
        file_name = Path(benchmark_name).name

        if property_type == "variables":
            # For CNF: uf<variables>-<clauses_ratio>.cnf
            # For QASM: <name>_<variables>.qasm
            m = re.search(r"uf(\d+)", file_name)
            if m:
                return int(m.group(1))
            m = re.search(r"_(\d+)\.qasm$", file_name, flags=re.IGNORECASE)
            if m:
                return int(m.group(1))
        
        elif property_type == "clauses":
            # For CNF/QASM names like uf20-0100.cnf / uf20-0100.qasm:
            # clause count is the numeric suffix right before extension.
            m = re.search(r"-(\d+)\.(?:cnf|qasm)$", file_name, flags=re.IGNORECASE)
            if m:
                return int(m.group(1))
        
        elif property_type == "aod_rows":
            # TODO: Extract from benchmark metadata if available
            pass
        
        return None

    def _collect_series(
        self, x_axis: str, y_metric: str
    ) -> Dict[str, Tuple[List[int], List[float]]]:
        """
        Collect data series for each compiler.
        
        Args:
            x_axis: One of 'variables', 'clauses', or 'aod_rows'
            y_metric: One of 'total_move_dist', 'trap_swap_count', or 'num_rydberg_activations'
        
        Returns:
            Dict mapping compiler name to (x_values, y_values)
        """
        if self.metrics_dir is None:
            raise ValueError("metrics_dir is required for x_axis 'variables' or 'clauses'")
        if not self.compiler_files:
            raise FileNotFoundError(f"No compiler metric JSON files found in {self.metrics_dir}")

        series: Dict[str, Tuple[List[int], List[float]]] = {}
        
        for compiler_file in self.compiler_files:
            try:
                payload = self._load_json(compiler_file)
            except Exception as e:
                logger.warning(f"Failed to load {compiler_file}: {e}")
                continue
            
            compiler_name = payload.get("compiler", compiler_file.stem)
            benchmarks = payload.get("benchmarks", [])
            runs = payload.get("runs", {})
            
            if not runs:
                logger.warning(f"No runs found in {compiler_file}")
                continue
            
            # Use first available run
            run_id = sorted(runs.keys())[0]
            run_data = runs[run_id]

            y_values = self._extract_metric_values(run_data, y_metric)
            
            if y_values is None:
                logger.warning(
                    f"Metric {y_metric} not found in {compiler_file} for run {run_id}"
                )
                continue
            
            # Collect points
            points: List[Tuple[int, float]] = []
            for bench_name, y_val in zip(benchmarks, y_values):
                x_val = self._extract_benchmark_property(bench_name, x_axis)
                if x_val is None or y_val is None:
                    continue
                
                try:
                    points.append((x_val, float(y_val)))
                except (ValueError, TypeError):
                    continue
            
            if points:
                points.sort(key=lambda t: t[0])
                x = [p[0] for p in points]
                y = [p[1] for p in points]
                series[compiler_name] = (x, y)
                logger.info(f"Loaded {len(points)} points for {compiler_name}")
        
        if not series:
            raise ValueError(f"No valid data series found for x_axis={x_axis}, y_metric={y_metric}")
        
        return series

    def _collect_series_aod_rows(
        self, aod_results_dir: Path, aod_variation: List[int], y_metric: str
    ) -> Dict[str, Tuple[List[int], List[float]]]:
        """
        Collect series when x-axis is AOD rows from multiple metrics/<timestamp>_arch folders.

        For each folder in `aod_results_dir`, aggregate each compiler's metric by mean over
        all benchmark values in the first run.
        """
        if not aod_results_dir.exists() or not aod_results_dir.is_dir():
            raise FileNotFoundError(f"AOD results folder not found: {aod_results_dir}")

        arch_dirs = sorted(
            d for d in aod_results_dir.iterdir() if d.is_dir() and d.name.endswith("_arch")
        )
        if not arch_dirs:
            raise FileNotFoundError(
                f"No <timestamp>_arch folders found in {aod_results_dir}"
            )

        if len(arch_dirs) != len(aod_variation):
            raise ValueError(
                "Length mismatch: number of <timestamp>_arch folders "
                f"({len(arch_dirs)}) != number of --aod-variation values ({len(aod_variation)})"
            )

        points_per_compiler: Dict[str, List[Tuple[int, float]]] = {}

        for arch_dir, aod_rows in zip(arch_dirs, aod_variation):
            compiler_files = sorted(arch_dir.glob("*.json"))
            if not compiler_files:
                logger.warning(f"No compiler metric JSON files found in {arch_dir}")
                continue

            for compiler_file in compiler_files:
                try:
                    payload = self._load_json(compiler_file)
                except Exception as e:
                    logger.warning(f"Failed to load {compiler_file}: {e}")
                    continue

                compiler_name = payload.get("compiler", compiler_file.stem)
                runs = payload.get("runs", {})
                if not runs:
                    logger.warning(f"No runs found in {compiler_file}")
                    continue

                run_id = sorted(runs.keys())[0]
                run_data = runs[run_id]
                y_values = self._extract_metric_values(run_data, y_metric)
                if not y_values:
                    logger.warning(
                        f"Metric {y_metric} not found in {compiler_file} for run {run_id}"
                    )
                    continue

                y_mean = sum(y_values) / len(y_values)
                points_per_compiler.setdefault(compiler_name, []).append((aod_rows, y_mean))

        series: Dict[str, Tuple[List[int], List[float]]] = {}
        for compiler_name, points in points_per_compiler.items():
            points.sort(key=lambda t: t[0])
            x_vals = [p[0] for p in points]
            y_vals = [p[1] for p in points]
            series[compiler_name] = (x_vals, y_vals)

        if not series:
            raise ValueError(
                "No valid data series found for AOD rows plotting. "
                "Check --aod-results and metric availability."
            )

        return series

    def plot(
        self,
        x_axis: str,
        y_metric: str,
        output_path: Optional[Path] = None,
        show: bool = False,
        aod_results_dir: Optional[Path] = None,
        aod_variation: Optional[List[int]] = None,
    ) -> Path:
        """
        Generate and save a plot.
        
        Args:
            x_axis: One of 'variables', 'clauses', or 'aod_rows'
            y_metric: One of 'total_move_dist', 'trap_swap_count', or 'num_rydberg_activations'
            output_path: Path to save the plot. If None, generates default name.
            show: Whether to display the plot interactively
        
        Returns:
            Path to saved plot
        """
        # Validate inputs
        valid_x_axes = ["variables", "clauses", "aod_rows"]
        valid_y_metrics = ["total_move_dist", "trap_swap_count", "num_rydberg_activations"]
        
        if x_axis not in valid_x_axes:
            raise ValueError(
                f"Invalid x_axis: {x_axis}. Must be one of {valid_x_axes}"
            )
        if y_metric not in valid_y_metrics:
            raise ValueError(
                f"Invalid y_metric: {y_metric}. Must be one of {valid_y_metrics}"
            )

        if x_axis == "aod_rows":
            if aod_results_dir is None or aod_variation is None:
                raise ValueError(
                    "For x_axis='aod_rows', both --aod-results and --aod-variation are required"
                )
        
        # Generate default output path if needed
        if output_path is None:
            if x_axis == "aod_rows":
                output_base = Path(aod_results_dir)
            elif self.metrics_dir is not None:
                output_base = self.metrics_dir
            else:
                raise ValueError("metrics_dir is required to generate default output path")

            output_dir = output_base.parent.parent / "plots"
            output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_path = output_dir / f"{y_metric}_vs_{x_axis}_{timestamp}.png"
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Collect data
        if x_axis == "aod_rows":
            series = self._collect_series_aod_rows(Path(aod_results_dir), aod_variation, y_metric)
        else:
            series = self._collect_series(x_axis, y_metric)
        
        # Generate plot
        plt.figure(figsize=(10, 6))
        
        style_cycle = [
            {"marker": "o", "linestyle": "-"},
            {"marker": "s", "linestyle": "--"},
            {"marker": "^", "linestyle": "-."},
            {"marker": "D", "linestyle": ":"},
            {"marker": "v", "linestyle": "-"},
            {"marker": "P", "linestyle": "--"},
        ]
        
        for i, (compiler_name, (x_vals, y_vals)) in enumerate(sorted(series.items())):
            style = style_cycle[i % len(style_cycle)]
            plt.plot(
                x_vals,
                y_vals,
                marker=style["marker"],
                markersize=4,
                linewidth=1.2,
                linestyle=style["linestyle"],
                alpha=0.8,
                markerfacecolor="white",
                markeredgewidth=0.9,
                label=compiler_name.upper(),
            )
        
        # Format axes
        x_label_map = {
            "variables": "Number of variables",
            "clauses": "Number of clauses",
            "aod_rows": "AOD rows",
        }
        
        y_label_map = {
            "total_move_dist": "Sum over moving distance (µm)",
            "trap_swap_count": "Trap swap count",
            "num_rydberg_activations": "Number of Rydberg activations",
        }
        
        plt.xlabel(x_label_map[x_axis])
        plt.ylabel(y_label_map[y_metric])

        if y_metric == "total_move_dist":
            ax = plt.gca()
            ax.yaxis.get_offset_text().set_visible(False)
            ax.yaxis.set_major_formatter(
                FuncFormatter(lambda value, _: f"{value:.0f}")
            )
            ax.set_ylim(bottom=0)

        else:
            plt.ylim(bottom=0)
        plt.grid(True, alpha=0.35)
        plt.legend()
        plt.tight_layout()
        
        # Save
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        if show:
            plt.show()
        else:
            plt.close()
        
        logger.info(f"Saved plot to {output_path}")
        return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plot metrics from a metrics/<timestamp>_arch folder"
    )
    parser.add_argument(
        "--metrics-dir",
        type=Path,
        default=None,
        help="Path to metrics/<timestamp>_arch folder",
    )
    parser.add_argument(
        "--aod-results",
        type=Path,
        default=None,
        help="Path to folder containing multiple <timestamp>_arch folders (used for --x-axis aod_rows)",
    )
    parser.add_argument(
        "--aod-variation",
        type=int,
        nargs="+",
        default=None,
        help="List of AOD-row values, one per <timestamp>_arch folder in sorted order (used for --x-axis aod_rows)",
    )
    parser.add_argument(
        "--x-axis",
        type=str,
        required=True,
        choices=["variables", "clauses", "aod_rows"],
        help="X-axis property",
    )
    parser.add_argument(
        "--y-metric",
        type=str,
        required=True,
        choices=["total_move_dist", "trap_swap_count", "num_rydberg_activations"],
        help="Y-axis metric",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output plot path (default: results/plots/{y_metric}_vs_{x_axis}.png)",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display plot interactively",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    
    try:
        if args.x_axis == "aod_rows":
            if args.aod_results is None or args.aod_variation is None:
                raise ValueError(
                    "When --x-axis aod_rows, you must provide both --aod-results and --aod-variation"
                )
            plotter = Plotter(args.metrics_dir)
        else:
            if args.metrics_dir is None:
                raise ValueError("--metrics-dir is required unless --x-axis is aod_rows")
            plotter = Plotter(args.metrics_dir)

        output = plotter.plot(
            x_axis=args.x_axis,
            y_metric=args.y_metric,
            output_path=args.output,
            show=args.show,
            aod_results_dir=args.aod_results,
            aod_variation=args.aod_variation,
        )
        print(f"Plot saved to {output}")
    except Exception as e:
        logger.error(f"Failed to generate plot: {e}")
        raise


if __name__ == "__main__":
    main()