"""Generate ES convergence plots from saved experiment CSV files."""

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from evolution_strategy.results import ALPHAS, DEFAULT_RESULTS_DIR, PORTFOLIOS
from logger import get_logger

logger = get_logger(__name__)


VARIANT_LABELS = {
    "one_plus_one": "(1+1)-ES",
    "ten_plus_seventy": "(10+70)-ES",
    "ten_comma_seventy": "(10,70)-ES",
}


def plot_convergence(dataset, alpha, results_root, budget=30000, num_runs=10):
    case = f"{dataset}_alpha{int(alpha * 100):03d}"
    results_dir = results_root / "full"

    fig, ax = plt.subplots(figsize=(8, 5))

    for variant, label in VARIANT_LABELS.items():
        folder = results_dir / (
            f"{case}_{variant}_e{budget}_r{num_runs}"
        )
        csv_path = folder / "convergence.csv"

        if not csv_path.exists():
            raise FileNotFoundError(
                f"Missing convergence data: {csv_path}"
            )

        with csv_path.open(
            newline="", encoding="utf-8"
        ) as handle:
            rows = list(csv.DictReader(handle))

        if len(rows) != budget:
            raise ValueError(
                f"{label}: expected {budget} evaluations, "
                f"found {len(rows)}"
            )

        evaluations = [
            int(row["evaluation"]) for row in rows
        ]
        mean_variance = [
            float(row["mean_best_variance"])
            for row in rows
        ]

        ax.plot(
            evaluations,
            mean_variance,
            color={
                "one_plus_one": "tab:blue",
                "ten_plus_seventy": "tab:orange",
                "ten_comma_seventy": "tab:green",
            }[variant],
            linestyle="--" if variant == "ten_comma_seventy" else "-",
            linewidth=2.2,
            label=label,
            zorder=3 if variant == "ten_comma_seventy" else 2,
        )

    ax.set_title(
        f"ES Convergence — {case} "
        f"({num_runs} seeds, {budget:,} evaluations)"
    )
    ax.set_xlabel("Objective evaluations")
    ax.set_ylabel(
        "Mean archive best-so-far portfolio variance"
    )

    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.ticklabel_format(
        axis="y", style="sci", scilimits=(-3, 3)
    )

    fig.tight_layout()

    output = results_root / "figures"
    output.mkdir(parents=True, exist_ok=True)

    filename = f"convergence_{case}_full"
    out_path = output / f"{filename}.png"

    fig.savefig(
        out_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)

    logger.info(f"Saved ES convergence plot: {out_path}")


def generate_all_plots_es(
    results_dir: Path | str = DEFAULT_RESULTS_DIR,
    dataset_figures_dir: Path | str | None = None,
) -> None:
    """Generate convergence, comparison, and dataset plots for ES results."""
    from evolution_strategy.plot_comparisons import (
        load_summary,
        plot_boxplot,
        plot_mean_variance,
        plot_runtime,
    )
    from evolution_strategy.plot_datasets import (
        DEFAULT_OUT_DIR as DEFAULT_DATASET_FIGURES_DIR,
        FIGURE_NAME as DATASET_FIGURE_NAME,
        plot_dataset_correlations,
    )

    results_root = Path(results_dir)

    for dataset in PORTFOLIOS:
        for alpha in ALPHAS:
            plot_convergence(dataset, alpha, results_root)

    summary = load_summary(results_root / "es_summary_45_cases.csv")
    figures_dir = results_root / "figures"
    plot_mean_variance(summary, figures_dir)
    plot_runtime(summary, figures_dir)
    plot_boxplot(summary, results_root, figures_dir)

    if dataset_figures_dir is not None:
        dataset_out_dir = Path(dataset_figures_dir)
    elif results_root == DEFAULT_RESULTS_DIR:
        dataset_out_dir = DEFAULT_DATASET_FIGURES_DIR
    else:
        dataset_out_dir = results_root / "figures"

    plot_dataset_correlations(
        PORTFOLIOS, dataset_out_dir / DATASET_FIGURE_NAME
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="port5")
    parser.add_argument("--alpha", type=float, default=0.50)
    parser.add_argument(
        "--results-dir", default=str(DEFAULT_RESULTS_DIR)
    )

    args = parser.parse_args()

    plot_convergence(
        args.dataset,
        args.alpha,
        Path(args.results_dir),
    )


if __name__ == "__main__":
    main()
