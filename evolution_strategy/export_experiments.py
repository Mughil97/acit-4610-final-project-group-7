"""Save ES experiment results case by case for reproducibility."""

import argparse
import csv
import json
import os
from pathlib import Path

from evolution_strategy.results import (
    ALPHAS,
    PORTFOLIOS,
    summarize_case,
)
from evolution_strategy.evolution_strategies import VARIANTS


def save_csv(path, columns, rows):
    """Write a CSV file, then replace the destination atomically."""
    temporary = path.with_name(path.name + ".tmp")

    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerows(rows)

    os.replace(temporary, path)


def export_case(summary, folder, budget):
    """Export statistics, individual runs, and convergence history."""
    folder.mkdir(parents=True, exist_ok=True)

    if len(summary.mean_history) != budget:
        raise ValueError("Incorrect convergence-history length")

    if any(len(run.history) != budget for run in summary.runs):
        raise ValueError("A run did not meet its evaluation budget")

    save_csv(
        folder / "summary.csv",
        [
            "dataset", "alpha", "variant", "num_runs",
            "evaluations", "best_variance", "mean_variance",
            "std_variance", "feasible_rate_percent",
            "mean_runtime_seconds", "best_weights_json",
        ],
        [[
            summary.dataset_name,
            summary.alpha,
            summary.variant,
            len(summary.runs),
            budget,
            summary.best_cost,
            summary.mean_cost,
            summary.std_cost,
            summary.feasible_rate,
            summary.mean_runtime,
            json.dumps(summary.best_weights),
        ]],
    )

    save_csv(
        folder / "runs.csv",
        [
            "seed", "final_variance", "portfolio_return",
            "target_return", "feasible", "runtime_seconds",
            "evaluations", "weights_json",
        ],
        (
            [
                run.seed,
                run.cost,
                run.profit,
                run.target_return,
                run.is_valid,
                run.runtime_seconds,
                len(run.history),
                json.dumps(run.weights),
            ]
            for run in summary.runs
        ),
    )

    save_csv(
        folder / "convergence.csv",
        ["evaluation", "mean_best_variance"],
        (
            [evaluation, value]
            for evaluation, value in enumerate(
                summary.mean_history, start=1
            )
        ),
    )

    # Written last: indicates that all three exports completed.
    marker = folder / "complete.json"
    temporary = folder / "complete.json.tmp"
    temporary.write_text(
        json.dumps({
            "status": "complete",
            "dataset": summary.dataset_name,
            "alpha": summary.alpha,
            "variant": summary.variant,
            "num_runs": len(summary.runs),
            "evaluations_per_run": budget,
        }, indent=2),
        encoding="utf-8",
    )
    os.replace(temporary, marker)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode", choices=["smoke", "full"], required=True
    )
    parser.add_argument(
        "--output", default="../es_experiment_results"
    )
    args = parser.parse_args()

    if args.mode == "smoke":
        portfolios = {"port1": PORTFOLIOS["port1"]}
        alphas = (0.50,)
        num_runs = 2
        budget = 83
    else:
        portfolios = PORTFOLIOS
        alphas = ALPHAS
        num_runs = 10
        budget = 30000

    output_root = Path(args.output) / args.mode

    for dataset_name, portfolio in portfolios.items():
        for alpha in alphas:
            for variant in VARIANTS:
                case_name = (
                    f"{dataset_name}_alpha{int(alpha * 100):03d}"
                    f"_{variant}_e{budget}_r{num_runs}"
                )
                folder = output_root / case_name

                if (folder / "complete.json").exists():
                    print(f"SKIP: {case_name}", flush=True)
                    continue

                print(f"RUN: {case_name}", flush=True)

                summary = summarize_case(
                    dataset_name=dataset_name,
                    portfolio=portfolio,
                    alpha=alpha,
                    variant=variant,
                    num_runs=num_runs,
                    max_iterations=budget,
                )

                export_case(summary, folder, budget)
                print(f"SAVED: {case_name}", flush=True)


if __name__ == "__main__":
    main()
