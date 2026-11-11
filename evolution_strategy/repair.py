"""Feasibility repair for long-only portfolio weights.

Correction 1: Euclidean simplex projection as specified in Portfolio 2026,
Problem 2, page 10. The existing return-target repair is preserved.
"""
import math

from evolution_strategy.portfolio import Portfolio
from evolution_strategy.evaluation import evaluate_profit


def project_simplex(weights: list[float]) -> list[float]:
    """Project a vector onto {w >= 0, sum(w) == 1} in Euclidean distance.

    Find theta with q_i = max(z_i - theta, 0), sum(q) = 1.
    Sorting-based implementation: O(n log n), no new dependencies.
    """
    if not weights:
        raise ValueError("Cannot project an empty weight vector")
    if not all(math.isfinite(value) for value in weights):
        raise ValueError("All portfolio weights must be finite")

    ordered = sorted(weights, reverse=True)
    running_sum = 0.0
    theta = 0.0

    for rank, value in enumerate(ordered, start=1):
        running_sum += value
        candidate_theta = (running_sum - 1.0) / rank
        if value > candidate_theta:
            theta = candidate_theta

    return [max(value - theta, 0.0) for value in weights]


def repair(portfolio: list[Portfolio], weights: list[float], target_return: float) -> list[float]:
    n = len(portfolio)

    # 1. Required Euclidean simplex projection (not clipping + normalization)
    weights = project_simplex(weights)

    # 2. If profit is below target_return, shift weight toward best-profit company
    current_profit = evaluate_profit(portfolio, weights)
    if current_profit >= target_return:
        return weights

    best_idx = max(range(n), key=lambda i: portfolio[i].profit)
    max_profit = portfolio[best_idx].profit

    if max_profit <= current_profit:
        return weights

    beta = min(1.0, (target_return - current_profit) / (max_profit - current_profit))
    weights = [(1.0 - beta) * w for w in weights]
    weights[best_idx] += beta
    return weights
