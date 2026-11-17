"""Generate ES convergence plots from saved experiment CSV files."""

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt


VARIANT_LABELS = {
    "one_plus_one": "(1+1)-ES",
    "ten_plus_seventy": "(10+70)-ES",
    "ten_comma_seventy": "(10,70)-ES",
}


def plot_convergence(mode, dataset, alpha, results_root):
    budget = 83 if mode == "smoke" else 30000
    num_runs = 2 if mode == "smoke" else 10

    case = f"{dataset}_alpha{int(alpha * 100):03d}"
    results_dir = results_root / mode

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

    filename = f"convergence_{case}_{mode}"

    fig.savefig(
        output / f"{filename}.png",
        dpi=300,
        bbox_inches="tight",
    )
    fig.savefig(
        output / f"{filename}.pdf",
        bbox_inches="tight",
    )

    plt.close(fig)

    print(f"Saved PNG: {output / (filename + '.png')}")
    print(f"Saved PDF: {output / (filename + '.pdf')}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode", choices=["smoke", "full"], required=True
    )
    parser.add_argument("--dataset", default="port5")
    parser.add_argument("--alpha", type=float, default=0.50)
    parser.add_argument(
        "--results-dir", default="../es_experiment_results"
    )

    args = parser.parse_args()

    plot_convergence(
        args.mode,
        args.dataset,
        args.alpha,
        Path(args.results_dir),
    )


if __name__ == "__main__":
    main()
