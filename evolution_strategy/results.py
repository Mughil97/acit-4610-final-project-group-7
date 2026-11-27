"""Execute and summarize portfolio ES experiments.

Runs seeded experiments and calculates solution quality,
feasibility, runtime, and convergence statistics.
"""
from dataclasses import dataclass, field
import math
from pathlib import Path

from evolution_strategy.evaluation import get_target_return
from evolution_strategy.evolution_strategies import (
    ESResult,
    VARIANTS,
    run_es,
)
from evolution_strategy.portfolio import (
    Portfolio,
    portfolio1,
    portfolio2,
    portfolio3,
    portfolio4,
    portfolio5,
)
from logger import get_logger

logger = get_logger(__name__)

DEFAULT_RESULTS_DIR = Path("evolution_strategy/results")

PORTFOLIOS: dict[str, list[Portfolio]] = {
    "port1": portfolio1,
    "port2": portfolio2,
    "port3": portfolio3,
    "port4": portfolio4,
    "port5": portfolio5,
}

ALPHAS: tuple[float, ...] = (0.25, 0.50, 0.75)

VARIANT_LABELS: dict[str, str] = {
    "one_plus_one": "(1+1)-ES",
    "ten_plus_seventy": "(10+70)-ES",
    "ten_comma_seventy": "(10,70)-ES",
}


@dataclass
class CaseSummary:
    """Store aggregated results for one experimental case.

    Each case represents one dataset, return target,
    and ES variant evaluated across multiple seeds.
    """
    case_name: str
    dataset_name: str
    alpha: float
    variant: str
    num_assets: int
    target_return: float
    best_cost: float
    mean_cost: float
    std_cost: float
    feasible_rate: float
    mean_runtime: float
    best_weights: list[float] = field(default_factory=list)
    mean_history: list[float] = field(default_factory=list)
    runs: list[ESResult] = field(default_factory=list)


def format_run_log(result: ESResult, run_idx: int, total_runs: int) -> str:
    """Format a single ES run log line with variance, return constraint, and timing."""
    initial_var = result.history[0] if result.history else result.cost
    ret_cmp = ">=" if result.profit >= result.target_return - 1e-8 else "<"
    return (
        f"  Run {run_idx:2d}/{total_runs} (seed {result.seed}) | "
        f"var: {initial_var:.4e} -> {result.cost:.4e} | "
        f"R(w)={result.profit:.6f} {ret_cmp} R*={result.target_return:.6f} | "
        f"feasible={str(result.is_valid):5s} | "
        f"evals={len(result.history)} | {result.runtime_seconds:.2f}s"
    )


def format_case_summary(summary: CaseSummary) -> str:
    """Format aggregated 10-run case metrics matching REQUIREMENTS.md."""
    label = VARIANT_LABELS.get(summary.variant, summary.variant)
    valid_count = sum(1 for run in summary.runs if run.is_valid)
    total_runs = len(summary.runs)
    return (
        f"Summary | {summary.case_name} | {label:10s} | "
        f"n={summary.num_assets:3d} | R*={summary.target_return:.6f} | "
        f"best={summary.best_cost:.5e} | mean={summary.mean_cost:.5e} | "
        f"std={summary.std_cost:.2e} | "
        f"feasible={valid_count}/{total_runs} ({summary.feasible_rate:5.1f}%) | "
        f"mean_time={summary.mean_runtime:.2f}s"
    )


def summarize_case(
        dataset_name: str,
        portfolio: list[Portfolio],
        alpha: float,
        variant: str,
        num_runs: int = 10,
        max_iterations: int = 30000,
) -> CaseSummary:
    """Execute repeated ES runs for one experimental case.

    Calculate variance statistics from feasible runs,
    runtime across all runs, and mean convergence history.
    """
    case_name = f"{dataset_name}_alpha{int(alpha * 100):03d}"
    runs: list[ESResult] = []

    # Use matching seeds for consistent algorithm comparisons.
    for seed in range(num_runs):
        result = run_es(
            portfolio=portfolio,
            alpha=alpha,
            variant=variant,
            max_iterations=max_iterations,
            seed=seed,
        )
        logger.info(format_run_log(result, seed + 1, num_runs))
        if not result.is_valid:
            logger.warning(
                f"  Infeasible solution on {case_name} ({VARIANT_LABELS.get(variant, variant)}, seed {seed}): "
                f"sum(w)={sum(result.weights):.8f}, min(w)={min(result.weights):.2e}, "
                f"R(w)={result.profit:.6f} < R*={result.target_return:.6f}"
            )
        runs.append(result)

    # Calculate solution-quality statistics from feasible runs.
    valid_runs = [run for run in runs if run.is_valid]
    valid_costs = [run.cost for run in valid_runs]

    if valid_costs:
        best_run = min(valid_runs, key=lambda run: run.cost)
        best_cost = best_run.cost
        best_weights = best_run.weights
        mean_cost = sum(valid_costs) / len(valid_costs)

        # Population standard deviation of final variances.
        std_cost = math.sqrt(
            sum((cost - mean_cost) ** 2 for cost in valid_costs) / len(valid_costs)
        )
    else:
        best_cost = float("inf")
        best_weights = []
        mean_cost = float("inf")
        std_cost = 0.0

    # Calculate feasibility rate and mean runtime across all runs.
    feasible_rate = 100.0 * len(valid_runs) / len(runs)
    mean_runtime = sum(run.runtime_seconds for run in runs) / len(runs)

    # Average convergence curve across all runs
    mean_history = [
        sum(run.history[step] for run in runs) / len(runs)
        for step in range(max_iterations)
    ]

    return CaseSummary(
        case_name=case_name,
        dataset_name=dataset_name,
        alpha=alpha,
        variant=variant,
        num_assets=len(portfolio),
        target_return=runs[0].target_return,
        best_cost=best_cost,
        mean_cost=mean_cost,
        std_cost=std_cost,
        feasible_rate=feasible_rate,
        mean_runtime=mean_runtime,
        best_weights=best_weights,
        mean_history=mean_history,
        runs=runs,
    )


def run_all_experiments(
        portfolios: dict[str, list[Portfolio]] = PORTFOLIOS,
        alphas: tuple[float, ...] = ALPHAS,
        variants: tuple[str, ...] = tuple(VARIANTS.keys()),
        num_runs: int = 10,
        max_iterations: int = 30000,
) -> list[CaseSummary]:
    """Execute the complete ES experimental design.

    Five datasets, three return targets, three ES variants,
    and ten seeds produce 45 cases and 450 runs by default.
    """
    all_summaries: list[CaseSummary] = []
    total_cases = len(portfolios) * len(alphas) * len(variants)
    case_idx = 0

    logger.info(
        f"========== Evolution Strategies — Portfolio Optimisation ({total_cases} cases, {num_runs} runs x {max_iterations} evals) =========="
    )
    for dataset_name, portfolio in portfolios.items():
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
                    num_runs=num_runs,
                    max_iterations=max_iterations,
                )
                all_summaries.append(summary)
                logger.info(format_case_summary(summary))

    return all_summaries
