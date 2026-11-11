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

VARIANTS = {
    "one_plus_one": run_one_plus_one,
    "ten_plus_seventy": run_ten_plus_seventy,
    "ten_comma_seventy": run_ten_comma_seventy,
}


@dataclass
class ESResult:
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
    if seed is not None:
        random.seed(seed)

    target_return = get_target_return(portfolio, alpha)
    start_time = perf_counter()

    weights, profit, cost, history = VARIANTS[variant](
        portfolio, target_return, max_iterations
    )

    runtime_seconds = perf_counter() - start_time
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
