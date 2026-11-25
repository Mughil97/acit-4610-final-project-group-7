"""Execution framework for portfolio Evolution Strategies.

Manages algorithm selection, return targets, random seeds,
runtime measurement, and portfolio feasibility validation.
"""

from dataclasses import dataclass, field
import random
from time import perf_counter

from evolution_strategy.algorithms import (
    run_one_plus_one,
    run_ten_comma_seventy,
    run_ten_plus_seventy,
)
from evolution_strategy.evaluation import (
    get_target_return,
)
from evolution_strategy.portfolio import (
    Portfolio,
)
from evolution_strategy.repair import repair


# Map variant names to their corresponding ES algorithms.
VARIANTS = {
    "one_plus_one": run_one_plus_one,
    "ten_plus_seventy": run_ten_plus_seventy,
    "ten_comma_seventy": run_ten_comma_seventy,
}


@dataclass
class ESResult:
    """Store the results of one ES experiment.

    Includes portfolio weights, expected return, variance,
    target return, runtime, feasibility, convergence history,
    and random seed.
    """

    variant: str
    weights: list[float]
    profit: float
    cost: float
    target_return: float
    runtime_seconds: float
    is_valid: bool
    history: list[float] = field(default_factory=list)
    seed: int | None = None


def is_feasible(
        weights: list[float],
        profit: float,
        target_return: float,
        tol: float = 1e-8,
) -> bool:
    """Validate the three portfolio constraints:

    - Non-negative weights.
    - Weights sum to one.
    - Expected return meets the minimum target.

    The tolerance accounts for floating-point rounding.
    """

    return (
        min(weights) >= -tol
        and abs(sum(weights) - 1.0) <= tol
        and profit >= target_return - tol
    )


def run_es(
        portfolio: list[Portfolio],
        alpha: float = 0.5,
        variant: str = "one_plus_one",
        max_iterations: int = 30000,
        seed: int | None = None,
) -> ESResult:
    """Run one ES experiment with a fixed evaluation budget.

    alpha determines the minimum return target.
    variant selects the Evolution Strategy.
    max_iterations represents objective evaluations,
    not generations.
    seed supports reproducibility.

    Returns the best portfolio and experimental metrics.
    """

    # Set the random seed for reproducibility.
    if seed is not None:
        random.seed(seed)

    # Calculate the minimum required expected return.
    target_return = get_target_return(portfolio, alpha)

    # Start measuring the algorithm's execution time.
    start_time = perf_counter()

    # Execute the selected ES variant.
    weights, profit, cost, history = VARIANTS[variant](
        portfolio, target_return, max_iterations
    )

    # Record the algorithm's elapsed runtime.
    runtime_seconds = perf_counter() - start_time

    # Validate the final portfolio constraints.
    valid = is_feasible(weights, profit, target_return)

    return ESResult(
        variant=variant,
        weights=weights,
        profit=profit,
        cost=cost,
        target_return=target_return,
        runtime_seconds=runtime_seconds,
        is_valid=valid,
        history=history,
        seed=seed,
    )
