"""Save ES experiment results case by case for reproducibility."""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
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


# =============================================================================
# BEGIN AI-ASSISTED SECTION
# Purpose: Parallelize ES case execution across CPU cores with ProcessPoolExecutor
#          (largest datasets scheduled first, single-threaded BLAS per worker),
#          always running all cases without skipping.
# =============================================================================
_DEFAULT_SUMMARIZE_CASE = summarize_case
_DEFAULT_EXPORT_CASE = export_case


def _init_worker() -> None:
    """Pin BLAS/OpenMP to 1 thread per worker to avoid thread oversubscription."""
    for env_var in (
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
    ):
        os.environ[env_var] = "1"


def _run_and_export_case(
    dataset_name: str,
    alpha: float,
    variant: str,
    folder: Path,
    num_runs: int,
    budget: int,
) -> str:
    portfolio = PORTFOLIOS[dataset_name]
    summary = _DEFAULT_SUMMARIZE_CASE(
        dataset_name=dataset_name,
        portfolio=portfolio,
        alpha=alpha,
        variant=variant,
        num_runs=num_runs,
        max_iterations=budget,
    )
    _DEFAULT_EXPORT_CASE(summary, folder, budget)
    return folder.name


def optimise_es(
    output_dir: Path | str = DEFAULT_RESULTS_DIR,
    portfolios=PORTFOLIOS,
    alphas=ALPHAS,
    num_runs: int = 10,
    budget: int = 30000,
    max_workers: int | None = None,
) -> Path:
    """Run all ES experiments in parallel, export CSVs, and rebuild the summary."""
    output_base = Path(output_dir)
    output_root = output_base / "full"

    logger.info(
        "==========  Evolution Strategies — Portfolio Optimisation (Problem 2) =========="
    )

    jobs: list[tuple[int, str, float, str, Path]] = []
    for dataset_name, portfolio in portfolios.items():
        for alpha in alphas:
            for variant in VARIANTS:
                case_name = (
                    f"{dataset_name}_alpha{int(alpha * 100):03d}"
                    f"_{variant}_e{budget}_r{num_runs}"
                )
                folder = output_root / case_name
                jobs.append((len(portfolio), dataset_name, alpha, variant, folder))

    workers = max_workers if max_workers is not None else min(len(jobs), os.cpu_count() or 1)
    can_parallelize = (
        workers > 1
        and len(jobs) > 1
        and portfolios is PORTFOLIOS
        and summarize_case is _DEFAULT_SUMMARIZE_CASE
        and export_case is _DEFAULT_EXPORT_CASE
    )

    if not can_parallelize:
        for _, dataset_name, alpha, variant, folder in jobs:
            logger.info(f"RUN: {folder.name}")
            summary = summarize_case(
                dataset_name=dataset_name,
                portfolio=portfolios[dataset_name],
                alpha=alpha,
                variant=variant,
                num_runs=num_runs,
                max_iterations=budget,
            )
            export_case(summary, folder, budget)
            logger.info(f"SAVED: {folder.name}")
    else:
        # Schedule largest portfolios first (port5 -> port1) for better load balance
        jobs.sort(key=lambda item: item[0], reverse=True)
        logger.info(f"Running {len(jobs)} ES cases across {workers} worker processes")
        with ProcessPoolExecutor(
            max_workers=workers, initializer=_init_worker
        ) as pool:
            futures = {
                pool.submit(
                    _run_and_export_case,
                    dataset_name,
                    alpha,
                    variant,
                    folder,
                    num_runs,
                    budget,
                ): folder.name
                for _, dataset_name, alpha, variant, folder in jobs
            }
            for future in as_completed(futures):
                logger.info(f"SAVED: {future.result()}")

    output_csv = output_base / SUMMARY_NAME
    count = build_summary(output_root, output_csv)
    logger.info(f"SUMMARY: {count} cases -> {output_csv}")

    return output_root


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", default=str(DEFAULT_RESULTS_DIR)
    )
    parser.add_argument(
        "--workers", type=int, default=None
    )
    args = parser.parse_args()
    optimise_es(output_dir=args.output, max_workers=args.workers)
# =============================================================================
# END AI-ASSISTED SECTION
# =============================================================================


if __name__ == "__main__":
    main()
