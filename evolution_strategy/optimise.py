"""Execute and export ES experiments for reproducibility.

Saves individual runs, summary statistics, and convergence
histories for every configured experimental case.
"""

import argparse
import csv
import json
import os
from pathlib import Path

from evolution_strategy.build_summary import SUMMARY_NAME, build_summary
from evolution_strategy.evaluation import get_target_return
from evolution_strategy.evolution_strategies import VARIANTS, run_es
from evolution_strategy.plot_results import generate_all_plots_es
from evolution_strategy.results import (
    ALPHAS,
    DEFAULT_RESULTS_DIR,
    PORTFOLIOS,
    VARIANT_LABELS,
    format_case_summary,
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
            "dataset",
            "alpha",
            "variant",
            "num_runs",
            "evaluations",
            "best_variance",
            "mean_variance",
            "std_variance",
            "feasible_rate_percent",
            "mean_runtime_seconds",
            "best_weights_json",
        ],
        [
            [
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
            ]
        ],
    )

    save_csv(
        folder / "runs.csv",
        [
            "seed",
            "final_variance",
            "portfolio_return",
            "target_return",
            "feasible",
            "runtime_seconds",
            "evaluations",
            "weights_json",
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
            for evaluation, value in enumerate(summary.mean_history, start=1)
        ),
    )

    # Preserve the complete best-so-far history of every seed.
    save_csv(
        folder / "run_histories.csv",
        ["evaluation"] + [f"seed_{run.seed}" for run in summary.runs],
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
        json.dumps(
            {
                "status": "complete",
                "dataset": summary.dataset_name,
                "alpha": summary.alpha,
                "variant": summary.variant,
                "num_runs": len(summary.runs),
                "evaluations_per_run": budget,
            },
            indent=2,
        ),
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
    """Execute ES experiments and export all cases.

    The default configuration produces 45 experimental cases
    and 450 runs across all datasets, targets, and variants.
    Every invocation recomputes and overwrites all configured cases.
    """
    output_root = Path(output_dir)
    total_cases = len(portfolios) * len(alphas) * len(VARIANTS)
    case_idx = 0

    logger.info(
        f"========== Evolution Strategies — Portfolio Optimisation ({total_cases} cases, {num_runs} runs x {budget} evals) =========="
    )
    for dataset_name, portfolio in portfolios.items():
        for alpha in alphas:
            target = get_target_return(portfolio, alpha)
            for variant in VARIANTS:
                case_idx += 1
                case_id = f"{dataset_name}_alpha{int(alpha * 100):03d}"
                folder_name = f"{case_id}_{variant}_e{budget}_r{num_runs}"
                folder = output_root / folder_name
                label = VARIANT_LABELS.get(variant, variant)

                logger.info(
                    f"[{case_idx}/{total_cases}] {case_id} | {label} | "
                    f"n={len(portfolio)} | alpha={alpha:.2f} | R*={target:.6f}"
                )

                summary = summarize_case(
                    dataset_name=dataset_name,
                    portfolio=portfolio,
                    alpha=alpha,
                    variant=variant,
                    num_runs=num_runs,
                    max_iterations=budget,
                )

                export_case(summary, folder, budget)
                logger.info(format_case_summary(summary))
                logger.info(f"Saved case outputs -> {folder}")

    # Consolidate completed cases into one experimental summary.
    output_csv = output_root / SUMMARY_NAME
    count = build_summary(output_root, output_csv)
    logger.info(f"Consolidated {count} ES cases -> {output_csv}")

    return output_root


# AI Assisted
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Problem 2 (Evolution Strategies): full 45-case set, one test case, or one seeded run."
    )
    parser.add_argument(
        "--dataset",
        choices=tuple(PORTFOLIOS.keys()),
        default=None,
        help="Run a single dataset (e.g., port1).",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        choices=ALPHAS,
        default=None,
        help="Return-target level alpha in {0.25, 0.50, 0.75}.",
    )
    parser.add_argument(
        "--variant",
        choices=tuple(VARIANTS.keys()),
        default=None,
        help="Single ES variant (defaults to all 3 variants for a test case).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Run a single seed (requires --dataset, --alpha, and --variant).",
    )
    args = parser.parse_args()

    if args.seed is not None:
        if not (args.dataset and args.alpha is not None and args.variant):
            parser.error("--seed requires --dataset, --alpha, and --variant.")
        portfolio = PORTFOLIOS[args.dataset]
        result = run_es(
            portfolio=portfolio,
            alpha=args.alpha,
            variant=args.variant,
            max_iterations=30000,
            seed=args.seed,
        )
        initial_var = result.history[0] if result.history else result.cost
        ret_cmp = ">=" if result.profit >= result.target_return - 1e-8 else "<"
        label = VARIANT_LABELS.get(args.variant, args.variant)
        logger.info(
            f"{args.dataset}_alpha{int(args.alpha * 100):03d} | {label} | "
            f"n={len(portfolio)} | seed={args.seed} | "
            f"var: {initial_var:.4e} -> {result.cost:.4e} | "
            f"R(w)={result.profit:.6f} {ret_cmp} R*={result.target_return:.6f} | "
            f"feasible={result.is_valid} | evals={len(result.history)} | "
            f"{result.runtime_seconds:.2f}s"
        )
        return

    if args.dataset is not None or args.alpha is not None or args.variant is not None:
        datasets = (args.dataset,) if args.dataset else tuple(PORTFOLIOS.keys())
        alphas = (args.alpha,) if args.alpha is not None else ALPHAS
        variants = (args.variant,) if args.variant else tuple(VARIANTS.keys())
        total_cases = len(datasets) * len(alphas) * len(variants)
        case_idx = 0

        for dataset_name in datasets:
            portfolio = PORTFOLIOS[dataset_name]
            for alpha in alphas:
                target = get_target_return(portfolio, alpha)
                for variant in variants:
                    case_idx += 1
                    label = VARIANT_LABELS.get(variant, variant)
                    logger.info(
                        f"[{case_idx}/{total_cases}] {dataset_name}_alpha{int(alpha * 100):03d} | "
                        f"{label} | n={len(portfolio)} | alpha={alpha:.2f} | R*={target:.6f}"
                    )
                    summary = summarize_case(
                        dataset_name=dataset_name,
                        portfolio=portfolio,
                        alpha=alpha,
                        variant=variant,
                        num_runs=10,
                        max_iterations=30000,
                    )
                    logger.info(format_case_summary(summary))
        return

    optimise_es()
    generate_all_plots_es()


if __name__ == "__main__":
    main()
# End AI Assisted
