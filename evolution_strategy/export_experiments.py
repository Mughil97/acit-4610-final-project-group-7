"""Execute and export ES experiments for reproducibility.

Saves individual runs, summary statistics, and convergence
histories. Supports resuming interrupted experiments by
skipping previously completed cases.
"""

import argparse
import csv
import json
import os
from pathlib import Path

from evolution_strategy.build_summary import SUMMARY_NAME, build_summary
from evolution_strategy.evolution_strategies import VARIANTS
from evolution_strategy.results import (
    ALPHAS,
    DEFAULT_RESULTS_DIR,
    PORTFOLIOS,
    summarize_case,
)
from logger import get_logger

logger = get_logger(__name__)


def save_csv(path, columns, rows):
    """Write a CSV file, then replace the destination atomically."""
    temporary = path.with_name(path.name + ".tmp")

    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerows(rows)

    os.replace(temporary, path)


def export_case(summary, folder, budget):
    """Export one completed experimental case.

    Files:
        summary.csv: Aggregated experimental statistics.
        runs.csv: Individual seeded run results.
        convergence.csv: Mean best-so-far convergence.
        run_histories.csv: Complete history of each seed.
        complete.json: Successful export marker.
    """
    folder.mkdir(parents=True, exist_ok=True)

    # Verify that every run respects the objective evaluation budget.
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

    # Preserve the complete best-so-far history of every seed.
    save_csv(
        folder / "run_histories.csv",
        ["evaluation"] + [
            f"seed_{run.seed}" for run in summary.runs
        ],
        (
            [evaluation, *values]
            for evaluation, values in enumerate(
                zip(*(run.history for run in summary.runs)),
                start=1,
            )
        ),
    )

    # Written last: indicates that all four CSV exports completed.
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


def optimise_es(
    output_dir: Path | str = DEFAULT_RESULTS_DIR,
    portfolios=PORTFOLIOS,
    alphas=ALPHAS,
    num_runs: int = 10,
    budget: int = 30000,
) -> Path:
    """Execute ES experiments and export completed cases.

    The default configuration produces 45 experimental cases
    and 450 runs across all datasets, targets, and variants.

    Existing completed cases are skipped. Use a separate
    output directory when evaluating a modified implementation.
    """
    output_base = Path(output_dir)
    output_root = output_base / "full"

    logger.info(
        "==========  Evolution Strategies — Portfolio Optimisation (Problem 2) =========="
    )
    for dataset_name, portfolio in portfolios.items():
        logger.info(f"Dataset: {dataset_name}")
        for alpha in alphas:
            logger.info(f"Alpha: {alpha:.2f}")
            for variant in VARIANTS:
                logger.info(f"Variant: {variant}")
                case_name = (
                    f"{dataset_name}_alpha{int(alpha * 100):03d}"
                    f"_{variant}_e{budget}_r{num_runs}"
                )
                folder = output_root / case_name

                required_files = (
                    "summary.csv",
                    "runs.csv",
                    "convergence.csv",
                    "run_histories.csv",
                    "complete.json",
                )

                # Resume interrupted experiments by skipping
                # cases with all required export files.
                # File existence does not verify algorithm version.
                if all(
                    (folder / filename).is_file()
                    for filename in required_files
                ):
                    logger.info(f"SKIP: {case_name}")
                    continue

                logger.info(f"RUN: {case_name}")

                summary = summarize_case(
                    dataset_name=dataset_name,
                    portfolio=portfolio,
                    alpha=alpha,
                    variant=variant,
                    num_runs=num_runs,
                    max_iterations=budget,
                )

                export_case(summary, folder, budget)
                logger.info(f"SAVED: {case_name}")

            logger.info("\n")

        logger.info(
            "------------------------------------------------------------------------------------\n"
        )

    # Consolidate completed cases into one experimental summary.
    output_csv = output_base / SUMMARY_NAME
    count = build_summary(output_root, output_csv)
    logger.info(f"SUMMARY: {count} cases -> {output_csv}")

    return output_root


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", default=str(DEFAULT_RESULTS_DIR)
    )
    args = parser.parse_args()
    optimise_es(output_dir=args.output)

if __name__ == "__main__":
    main()
