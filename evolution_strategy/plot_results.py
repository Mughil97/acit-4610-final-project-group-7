"""Generate ES convergence and comparison plots from saved results.

Reads exported CSV files and creates the required port5_alpha050
convergence plot along with summary, runtime, and boxplot figures.
"""

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from evolution_strategy.results import DEFAULT_RESULTS_DIR
from logger import get_logger

logger = get_logger(__name__)


VARIANT_LABELS = {
    "one_plus_one": "(1+1)-ES",
    "ten_plus_seventy": "(10+70)-ES",
    "ten_comma_seventy": "(10,70)-ES",
}


def plot_convergence(dataset, alpha, results_root, budget=30000, num_runs=10):
    """Plot mean convergence for one dataset and return target.

    Compare the three ES variants using saved convergence
    histories and verify the expected number of evaluations.
    """
    case = f"{dataset}_alpha{int(alpha * 100):03d}"
    results_root = Path(results_root)

    fig, ax = plt.subplots(figsize=(8, 5))

    for variant, label in VARIANT_LABELS.items():
        folder = results_root / (
            f"{case}_{variant}_e{budget}_r{num_runs}"
        )
        csv_path = folder / "convergence.csv"

        if not csv_path.exists():
            raise FileNotFoundError(
                f"Missing convergence data: {csv_path}"
            )

        # Read the saved mean best-so-far convergence history.
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
) -> None:
    """Generate all ES figures from saved experimental results.

    Creates the required port5_alpha050 convergence plot, summary
    comparison plots, runtime plots, and boxplots.
    """
    from evolution_strategy.plot_comparisons import (
        load_summary,
        plot_boxplot,
        plot_mean_variance,
        plot_runtime,
    )

    results_root = Path(results_dir)

    # Required convergence plot: port5_alpha050 only (REQUIREMENTS.md).
    plot_convergence("port5", 0.50, results_root)

    summary = load_summary(results_root / "es_summary_45_cases.csv")
    figures_dir = results_root / "figures"
    plot_mean_variance(summary, figures_dir)
    plot_runtime(summary, figures_dir)
    plot_boxplot(summary, results_root, figures_dir)


def main():
    """Generate all ES plots from saved results."""
    generate_all_plots_es()


if __name__ == "__main__":
    main()
