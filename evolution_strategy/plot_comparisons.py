"""Generate report-ready comparisons from saved ES experiment CSVs.

Run from the repository root::

    python -m evolution_strategy.plot_comparisons

The default experiment results folder is a sibling of the repository worktree:
../es_experiment_results. This script does NOT rerun optimization.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


DATASETS = ("port1", "port2", "port3", "port4", "port5")
ALPHAS = (0.25, 0.50, 0.75)
VARIANTS = (
    "one_plus_one",
    "ten_plus_seventy",
    "ten_comma_seventy",
)
LABELS = {
    "one_plus_one": "(1+1)-ES",
    "ten_plus_seventy": "(10+70)-ES",
    "ten_comma_seventy": "(10,70)-ES",
}
COLORS = {
    "one_plus_one": "tab:blue",
    "ten_plus_seventy": "tab:orange",
    "ten_comma_seventy": "tab:green",
}
LINESTYLES = {
    "one_plus_one": "-",
    "ten_plus_seventy": "-",
    "ten_comma_seventy": "--",
}
SUMMARY_COLUMNS = {
    "dataset", "alpha", "variant", "num_assets", "target_return",
    "num_runs", "evaluations_per_run", "best_variance", "mean_variance",
    "std_variance", "feasible_rate_percent", "mean_runtime_seconds",
}


def load_summary(csv_path: Path) -> dict[tuple[str, float, str], dict]:
    """Read the complete 45-case summary and validate its experiment grid."""
    if not csv_path.is_file():
        raise FileNotFoundError(
            f"Missing {csv_path}. Create es_summary_45_cases.csv first."
        )
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = SUMMARY_COLUMNS - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"Missing summary columns: {sorted(missing)}")
        records = list(reader)
    indexed = {}
    for record in records:
        key = (record["dataset"], float(record["alpha"]), record["variant"])
        if key in indexed:
            raise ValueError(f"Duplicate summary case: {key}")
        if key[0] not in DATASETS or key[1] not in ALPHAS or key[2] not in VARIANTS:
            raise ValueError(f"Unexpected summary case: {key}")
        if int(record["num_runs"]) != 10 or int(record["evaluations_per_run"]) != 30000:
            raise ValueError(f"Unexpected evaluation budget or seed count: {key}")
        for column in ("mean_variance", "best_variance", "std_variance",
                       "mean_runtime_seconds", "feasible_rate_percent"):
            value = float(record[column])
            if not math.isfinite(value):
                raise ValueError(f"Non-finite {column} in {key}")
        if float(record["mean_variance"]) <= 0:
            raise ValueError(f"Nonpositive mean variance for log-scale plot: {key}")
        indexed[key] = record
    expected = {(ds, a, v) for ds in DATASETS for a in ALPHAS for v in VARIANTS}
    missing = expected - set(indexed)
    if missing:
        raise ValueError(f"Incomplete summary: missing {len(missing)} cases; first {sorted(missing)[0]}")
    if len(indexed) != len(expected):
        raise ValueError("Expected exactly 45 cases")
    return indexed


def _save(fig, figures_dir: Path, filename: str) -> None:
    figures_dir.mkdir(parents=True, exist_ok=True)
    for extension, kwargs in (("png", {"dpi": 300}), ("pdf", {})):
        path = figures_dir / f"{filename}.{extension}"
        fig.savefig(path, bbox_inches="tight", **kwargs)
        print(f"Saved {path}")
    plt.close(fig)


def plot_mean_variance(summary: dict, figures_dir: Path) -> None:
    """Compare raw mean final variance across datasets, separated by alpha."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8), sharey=True)
    x = list(range(len(DATASETS)))
    for ax, alpha in zip(axes, ALPHAS):
        for variant in VARIANTS:
            values = [float(summary[(ds, alpha, variant)]["mean_variance"]) for ds in DATASETS]
            ax.plot(
                x, values, label=LABELS[variant], color=COLORS[variant],
                linestyle=LINESTYLES[variant], linewidth=2, marker="o", markersize=5,
            )
        ax.set_title(f"$\\alpha = {alpha:.2f}$")
        ax.set_xticks(x, DATASETS)
        ax.set_yscale("log")
        ax.grid(True, which="major", alpha=0.25)
        ax.set_xlabel("Benchmark dataset")
    axes[0].set_ylabel("Mean final portfolio variance (log scale)")
    fig.suptitle("Final variance across the five portfolio benchmarks (10 seeds/case)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False,
               bbox_to_anchor=(0.5, -0.04))
    fig.tight_layout(rect=(0, 0.08, 1, 0.95))
    _save(fig, figures_dir, "mean_variance_by_dataset_full")


def plot_runtime(summary: dict, figures_dir: Path) -> None:
    """Average per-run runtime across the three alpha settings for each dataset."""
    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    x = list(range(len(DATASETS)))
    sizes = [int(summary[(ds, ALPHAS[0], VARIANTS[0])]["num_assets"]) for ds in DATASETS]
    for variant in VARIANTS:
        values = [
            sum(float(summary[(ds, a, variant)]["mean_runtime_seconds"]) for a in ALPHAS)
            / len(ALPHAS)
            for ds in DATASETS
        ]
        ax.plot(x, values, label=LABELS[variant], color=COLORS[variant],
                linestyle=LINESTYLES[variant], linewidth=2.2, marker="o", markersize=7)
    ax.set_xticks(x, [f"{ds}\n({n} assets)" for ds, n in zip(DATASETS, sizes)])
    ax.set_ylabel("Mean runtime per run (seconds)")
    ax.set_xlabel("Benchmark dataset and asset count")
    ax.set_title("Runtime comparison (mean across the three return targets)")
    ax.set_ylim(bottom=0)
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend(loc="upper left")
    fig.tight_layout()
    _save(fig, figures_dir, "runtime_by_dataset_full")


def load_seed_variances(
    results_dir: Path, summary: dict, dataset: str, alpha: float
) -> dict[str, list[float]]:
    """Load genuine per-seed final variances; never infer them from summary stats."""
    values_by_variant = {}
    for variant in VARIANTS:
        record = summary[(dataset, alpha, variant)]
        budget = int(record["evaluations_per_run"])
        runs = int(record["num_runs"])
        folder = results_dir / "full" / (
            f"{dataset}_alpha{int(alpha * 100):03d}_{variant}_e{budget}_r{runs}"
        )
        runs_file = folder / "runs.csv"
        if not runs_file.is_file():
            raise FileNotFoundError(
                f"Missing actual per-seed results: {runs_file}. "
                "Copy/run this plotting script on the PC with your full results folder. "
                "Do not invent boxplot points from the summary."
            )
        with runs_file.open(newline="", encoding="utf-8-sig") as handle:
            records = list(csv.DictReader(handle))
        if len(records) != runs:
            raise ValueError(f"Expected {runs} seeds in {runs_file}, got {len(records)}")
        by_seed = {}
        for item in records:
            seed = int(item["seed"])
            if seed in by_seed:
                raise ValueError(f"Duplicate seed {seed} in {runs_file}")
            if int(item["evaluations"]) != budget:
                raise ValueError(f"Incorrect evaluation count for seed {seed} in {runs_file}")
            if str(item["feasible"]).lower() not in {"true", "1"}:
                raise ValueError(f"Infeasible seed {seed} in {runs_file}; review the result")
            val = float(item["final_variance"])
            if not math.isfinite(val):
                raise ValueError(f"Non-finite variance for seed {seed} in {runs_file}")
            by_seed[seed] = val
        if set(by_seed) != set(range(runs)):
            raise ValueError(f"Missing expected seeds 0..{runs-1} in {runs_file}")
        final_values = [by_seed[seed] for seed in range(runs)]
        actual_mean = sum(final_values) / runs
        if not math.isclose(actual_mean, float(record["mean_variance"]),
                            rel_tol=1e-8, abs_tol=1e-12):
            raise ValueError(f"Mean of runs.csv disagrees with summary.csv for {folder.name}")
        values_by_variant[variant] = final_values
    return values_by_variant


def plot_boxplot(summary: dict, results_dir: Path, figures_dir: Path,
                 dataset: str = "port5", alpha: float = 0.50) -> None:
    """Plot actual seed-level results with explicit axes and a proper legend."""
    values_by_variant = load_seed_variances(results_dir, summary, dataset, alpha)
    fig, ax = plt.subplots(figsize=(9.2, 5.8))

    # Display values in units of 10^-3 while retaining raw variance in CSVs.
    scaled_values = [
        [value * 1e3 for value in values_by_variant[variant]]
        for variant in VARIANTS
    ]
    boxplot = ax.boxplot(
        scaled_values,
        widths=0.48,
        patch_artist=True,
        showmeans=True,
        showfliers=False,  # Every seed is already shown as a colored dot.
        meanprops={
            "marker": "D", "markerfacecolor": "black",
            "markeredgecolor": "black", "markersize": 6,
        },
        medianprops={"color": "black", "linewidth": 1.8},
        whiskerprops={"color": "0.3", "linewidth": 1.2},
        capprops={"color": "0.3", "linewidth": 1.2},
    )

    for variant, patch in zip(VARIANTS, boxplot["boxes"]):
        patch.set_facecolor(COLORS[variant])
        patch.set_edgecolor(COLORS[variant])
        patch.set_alpha(0.25)

    for position, variant in enumerate(VARIANTS, start=1):
        # Deterministic offsets: show the exact ten recorded seeds, no random jitter.
        n_seeds = len(values_by_variant[variant])
        offsets = [((seed % 5) - 2) * 0.035 for seed in range(n_seeds)]
        ax.scatter(
            [position + offset for offset in offsets],
            scaled_values[position - 1],
            color=COLORS[variant], s=34, alpha=0.78,
            edgecolors="white", linewidths=0.35, zorder=4,
        )

    ax.set_xticks(range(1, len(VARIANTS) + 1),
                  [LABELS[variant] for variant in VARIANTS])
    ax.set_xlabel("Evolution Strategy variant")
    ax.set_ylabel(r"Final portfolio variance ($\times 10^{-3}$)")
    ax.set_title(
        f"Final portfolio variance across 10 seeds — {dataset}, "
        fr"$\alpha = {alpha:.2f}$"
    )
    ax.set_xlim(0.5, len(VARIANTS) + 0.5)
    ax.grid(True, axis="y", alpha=0.3)
    ax.set_axisbelow(True)

    # Explain the graphical statistics rather than repeating the x-axis labels.
    legend_handles = [
        Patch(facecolor="0.6", edgecolor="0.4", alpha=0.25,
              label="Box: 25th–75th percentile"),
        Line2D([0], [0], color="black", linewidth=1.8,
               label="Median (line)"),
        Line2D([0], [0], linestyle="None", marker="D", color="black",
               markersize=6, label="Mean (diamond)"),
        Line2D([0], [0], linestyle="None", marker="o", color="0.4",
               markersize=6, label="Individual seed (dot)"),
    ]
    fig.legend(
        handles=legend_handles, loc="lower center", ncol=4,
        bbox_to_anchor=(0.5, 0.025), frameon=False, fontsize=9,
    )
    # Reserve a dedicated band beneath the x-axis for the legend.
    fig.tight_layout(rect=(0, 0.14, 1, 1))
    _save(fig, figures_dir, f"boxplot_{dataset}_alpha{int(alpha * 100):03d}_full")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=Path("../es_experiment_results"))
    parser.add_argument("--dataset", choices=DATASETS, default="port5")
    parser.add_argument("--alpha", type=float, choices=ALPHAS, default=0.50)
    parser.add_argument("--summary-only", action="store_true",
                        help="Make the two summary-level plots without loading per-seed runs.csv")
    args = parser.parse_args()
    summary = load_summary(args.results_dir / "es_summary_45_cases.csv")
    figures_dir = args.results_dir / "figures"
    plot_mean_variance(summary, figures_dir)
    plot_runtime(summary, figures_dir)
    if not args.summary_only:
        plot_boxplot(summary, args.results_dir, figures_dir, args.dataset, args.alpha)
    print("Done. No optimization runs were executed.")


if __name__ == "__main__":
    main()
