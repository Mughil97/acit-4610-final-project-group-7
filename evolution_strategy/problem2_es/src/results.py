from dataclasses import dataclass, field
import math

from evolution_strategy.problem2_es.src.evolution_strategies import (
    ESResult,
    VARIANTS,
    run_es,
)
from evolution_strategy.problem2_es.src.portfolio import (
    Portfolio,
    portfolio1,
    portfolio2,
    portfolio3,
    portfolio4,
    portfolio5,
)

PORTFOLIOS: dict[str, list[Portfolio]] = {
    "port1": portfolio1,
    "port2": portfolio2,
    "port3": portfolio3,
    "port4": portfolio4,
    "port5": portfolio5,
}

ALPHAS: tuple[float, ...] = (0.25, 0.50, 0.75)


@dataclass
class CaseSummary:
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


def summarize_case(
        dataset_name: str,
        portfolio: list[Portfolio],
        alpha: float,
        variant: str,
        num_runs: int = 10,
        max_iterations: int = 1000,
) -> CaseSummary:
    case_name = f"{dataset_name}_alpha{int(alpha * 100):03d}"
    runs: list[ESResult] = []

    for seed in range(num_runs):
        result = run_es(
            portfolio=portfolio,
            alpha=alpha,
            variant=variant,
            max_iterations=max_iterations,
            seed=seed,
        )
        runs.append(result)

    valid_runs = [run for run in runs if run.is_valid]
    valid_costs = [run.cost for run in valid_runs]

    if valid_costs:
        best_run = min(valid_runs, key=lambda run: run.cost)
        best_cost = best_run.cost
        best_weights = best_run.weights
        mean_cost = sum(valid_costs) / len(valid_costs)
        std_cost = math.sqrt(
            sum((cost - mean_cost) ** 2 for cost in valid_costs) / len(valid_costs)
        )
    else:
        best_cost = float("inf")
        best_weights = []
        mean_cost = float("inf")
        std_cost = 0.0

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
        max_iterations: int = 1000,
) -> list[CaseSummary]:
    all_summaries: list[CaseSummary] = []

    for dataset_name, portfolio in portfolios.items():
        for alpha in alphas:
            for variant in variants:
                summary = summarize_case(
                    dataset_name=dataset_name,
                    portfolio=portfolio,
                    alpha=alpha,
                    variant=variant,
                    num_runs=num_runs,
                    max_iterations=max_iterations,
                )
                all_summaries.append(summary)
                print(
                    f"{summary.case_name:14s} | {summary.variant:17s} | "
                    f"n={summary.num_assets:3d} | R*={summary.target_return:.6f} | "
                    f"best={summary.best_cost:.6f} | mean={summary.mean_cost:.6f} | "
                    f"std={summary.std_cost:.6f} | valid={summary.feasible_rate:5.1f}% | "
                    f"time={summary.mean_runtime:.3f}s"
                )

    return all_summaries
