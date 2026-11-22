# =============================================================================
# BEGIN AI-ASSISTED SECTION
# Purpose: Vectorized NumPy implementations of (1+1)-ES, (10+70)-ES, and
#          (10,70)-ES using precomputed covariance matrices, batch simplex
#          projection/repair, and np.random.Generator.
# =============================================================================
import math
import numpy as np

from evolution_strategy.evaluation import (
    ProfitData,
    evaluate_batch_cost,
    get_covariance_matrix,
    get_profit_data,
)
from evolution_strategy.portfolio import Portfolio
from evolution_strategy.repair import repair_1d, repair_batch

_SUCCESS_FACTOR = math.exp(1.0 / 3.0)
_FAILURE_FACTOR = math.exp(-1.0 / 12.0)


def _evaluate_candidate_1d(
    weights: np.ndarray,
    profit_data: ProfitData,
    cov: np.ndarray,
    target_return: float,
) -> tuple[float, float, np.ndarray]:
    repaired_weights, profit = repair_1d(weights, profit_data, target_return)
    cost = float(repaired_weights @ (cov @ repaired_weights))
    return profit, cost, repaired_weights


def _evaluate_candidates_batch(
    weights_batch: np.ndarray,
    profit_data: ProfitData,
    cov: np.ndarray,
    target_return: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    repaired_weights, profits = repair_batch(
        weights_batch, profit_data, target_return
    )
    costs = evaluate_batch_cost(cov, repaired_weights)
    return profits, costs, repaired_weights


def update_one_plus_one_sigma(sigma: float, improved: bool) -> float:
    """Apply the assignment's per-trial 1/5-success-rule update.

    The step size is increased after a strictly better child and decreased
    otherwise, with the specified bounds [1e-8, 1.0].
    """
    factor = _SUCCESS_FACTOR if improved else _FAILURE_FACTOR
    return max(1e-8, min(1.0, sigma * factor))


def run_one_plus_one(
    portfolio: list[Portfolio],
    target_return: float,
    max_iterations: int = 30000,
    sigma: float | None = None,
    rng: np.random.Generator | None = None,
):
    """Run (1+1)-ES, counting initialization as one evaluation.

    In accordance with Portfolio 2026, Problem 2, p. 10, accept only strictly
    lower-variance offspring and update sigma after EACH evaluated child.
    """
    if rng is None:
        rng = np.random.default_rng()

    n = len(portfolio)
    profit_data = get_profit_data(portfolio)
    cov = get_covariance_matrix(portfolio)

    if sigma is None:
        sigma = 0.1 / math.sqrt(n)
    sigma = max(1e-8, min(1.0, sigma))

    current_profit, current_cost, current_weights = _evaluate_candidate_1d(
        rng.uniform(0.0, 1.0, size=n), profit_data, cov, target_return
    )
    history = np.empty(max_iterations, dtype=np.float64)
    history[0] = current_cost

    chunk_size = 4096
    step = 1
    while step < max_iterations:
        batch = min(chunk_size, max_iterations - step)
        noise = rng.standard_normal(size=(batch, n))
        for k in range(batch):
            candidate = current_weights + sigma * noise[k]
            new_profit, new_cost, repaired_weights = _evaluate_candidate_1d(
                candidate, profit_data, cov, target_return
            )

            improved = new_cost < current_cost  # strict improvement only
            if improved:
                current_weights = repaired_weights
                current_profit = new_profit
                current_cost = new_cost

            history[step] = current_cost
            sigma = update_one_plus_one_sigma(sigma, improved)
            step += 1

    return current_weights.tolist(), current_profit, current_cost, history.tolist()


def _run_population_es(
    portfolio: list[Portfolio],
    target_return: float,
    max_iterations: int,
    mu: int,
    lambda_: int,
    *,
    plus_selection: bool,
    rng: np.random.Generator | None = None,
):
    if rng is None:
        rng = np.random.default_rng()

    n = len(portfolio)
    profit_data = get_profit_data(portfolio)
    cov = get_covariance_matrix(portfolio)

    init_sigma = 0.1 / math.sqrt(n)
    tau_prime = 1.0 / math.sqrt(2.0 * n)
    tau = 1.0 / math.sqrt(2.0 * math.sqrt(n))

    init_count = min(mu, max_iterations)
    pop_p, pop_c, pop_w = _evaluate_candidates_batch(
        rng.uniform(0.0, 1.0, size=(init_count, n)),
        profit_data,
        cov,
        target_return,
    )
    pop_s = np.full((init_count, n), init_sigma, dtype=np.float64)

    history = np.empty(max_iterations, dtype=np.float64)
    history[:init_count] = np.minimum.accumulate(pop_c)

    best_idx = int(np.argmin(pop_c))
    best_cost = float(pop_c[best_idx])
    best_weights = pop_w[best_idx].copy()
    best_profit = float(pop_p[best_idx])

    evaluations = init_count

    while evaluations < max_iterations:
        bs = min(lambda_, max_iterations - evaluations)

        # 1. Sample 2 distinct parents uniformly at random for each offspring
        p1 = rng.integers(0, mu, size=bs)
        p2 = rng.integers(0, mu - 1, size=bs)
        p2 += p2 >= p1

        # 2. Recombine weights (arithmetic) and sigmas (geometric)
        child_w = 0.5 * (pop_w[p1] + pop_w[p2])
        child_s = np.sqrt(pop_s[p1] * pop_s[p2])

        # 3. Mutate sigmas (log-normal self-adaptation) and weights
        z0 = rng.standard_normal(size=(bs, 1))
        child_s *= np.exp(tau_prime * z0 + tau * rng.standard_normal(size=(bs, n)))
        np.clip(child_s, 1e-8, 1.0, out=child_s)
        child_w += child_s * rng.standard_normal(size=(bs, n))

        # 4. Evaluate entire offspring batch together
        child_p, child_c, child_w = _evaluate_candidates_batch(
            child_w, profit_data, cov, target_return
        )

        # 5. Record monotonic best-so-far archive history
        history[evaluations : evaluations + bs] = np.minimum(
            best_cost, np.minimum.accumulate(child_c)
        )
        batch_best_idx = int(np.argmin(child_c))
        if child_c[batch_best_idx] < best_cost:
            best_cost = float(child_c[batch_best_idx])
            best_weights = child_w[batch_best_idx].copy()
            best_profit = float(child_p[batch_best_idx])

        evaluations += bs

        # 6. Survivor selection: (mu + lambda) or (mu, lambda)
        if plus_selection:
            all_c = np.concatenate((pop_c, child_c))
            sel = np.argpartition(all_c, mu - 1)[:mu]
            pop_w = np.vstack((pop_w, child_w))[sel]
            pop_s = np.vstack((pop_s, child_s))[sel]
            pop_p = np.concatenate((pop_p, child_p))[sel]
            pop_c = all_c[sel]
        elif bs >= mu:
            if bs > mu:
                sel = np.argpartition(child_c, mu - 1)[:mu]
                pop_w = child_w[sel]
                pop_s = child_s[sel]
                pop_p = child_p[sel]
                pop_c = child_c[sel]
            else:
                pop_w, pop_s, pop_p, pop_c = child_w, child_s, child_p, child_c

    return best_weights.tolist(), best_profit, best_cost, history.tolist()


# (10+70)-ES Algorithm
def run_ten_plus_seventy(
    portfolio: list[Portfolio],
    target_return: float,
    max_iterations: int = 30000,
    mu: int = 10,
    lambda_: int = 70,
    rng: np.random.Generator | None = None,
):
    return _run_population_es(
        portfolio,
        target_return,
        max_iterations,
        mu,
        lambda_,
        plus_selection=True,
        rng=rng,
    )


# (10,70)-ES Algorithm
def run_ten_comma_seventy(
    portfolio: list[Portfolio],
    target_return: float,
    max_iterations: int = 30000,
    mu: int = 10,
    lambda_: int = 70,
    rng: np.random.Generator | None = None,
):
    return _run_population_es(
        portfolio,
        target_return,
        max_iterations,
        mu,
        lambda_,
        plus_selection=False,
        rng=rng,
    )
# =============================================================================
# END AI-ASSISTED SECTION
# =============================================================================
