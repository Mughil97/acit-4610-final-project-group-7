"""Feasibility repair for long-only portfolio weights.

Correction 1: Euclidean simplex projection as specified in Portfolio 2026,
Problem 2, page 10. The existing return-target repair is preserved.
"""
# =============================================================================
# BEGIN AI-ASSISTED SECTION
# Purpose: Vectorized 1D and 2D (batch) NumPy Euclidean simplex projection and
#          target-return repair, preserving list[float] wrapper compatibility.
# =============================================================================
import numpy as np

from evolution_strategy.evaluation import ProfitData, get_profit_data
from evolution_strategy.portfolio import Portfolio


def project_simplex_1d(weights: np.ndarray) -> np.ndarray:
    """Project a 1D vector onto {w >= 0, sum(w) == 1} in Euclidean distance."""
    if weights.size == 0:
        raise ValueError("Cannot project an empty weight vector")
    if not np.isfinite(weights).all():
        raise ValueError("All portfolio weights must be finite")

    ordered = np.sort(weights)[::-1]
    cssv = np.cumsum(ordered) - 1.0
    ranks = np.arange(1, weights.size + 1, dtype=np.float64)
    rho = int(np.nonzero(ordered - cssv / ranks > 0)[0][-1])
    theta = cssv[rho] / (rho + 1.0)
    return np.maximum(weights - theta, 0.0)


def project_simplex_batch(weights_batch: np.ndarray) -> np.ndarray:
    """Project each row of a (batch_size, n) array onto the Euclidean simplex."""
    if weights_batch.ndim != 2 or weights_batch.shape[1] == 0:
        raise ValueError("Cannot project an empty weight vector")
    if not np.isfinite(weights_batch).all():
        raise ValueError("All portfolio weights must be finite")

    ordered = np.sort(weights_batch, axis=1)[:, ::-1]
    cssv = np.cumsum(ordered, axis=1) - 1.0
    ranks = np.arange(1, weights_batch.shape[1] + 1, dtype=np.float64)
    cond = ordered - cssv / ranks > 0
    rho = weights_batch.shape[1] - 1 - np.argmax(cond[:, ::-1], axis=1)
    theta = cssv[np.arange(weights_batch.shape[0]), rho] / (rho + 1.0)
    return np.maximum(weights_batch - theta[:, None], 0.0)


def repair_1d(
    weights: np.ndarray,
    profit_data: ProfitData,
    target_return: float,
) -> tuple[np.ndarray, float]:
    w = project_simplex_1d(weights)
    current_profit = float(w @ profit_data.profits)

    if current_profit < target_return and profit_data.max_profit > current_profit:
        beta = min(
            1.0,
            (target_return - current_profit) / (profit_data.max_profit - current_profit),
        )
        w *= 1.0 - beta
        w[profit_data.best_idx] += beta
        current_profit = float(w @ profit_data.profits)

    return w, current_profit


def repair_batch(
    weights_batch: np.ndarray,
    profit_data: ProfitData,
    target_return: float,
) -> tuple[np.ndarray, np.ndarray]:
    w = project_simplex_batch(weights_batch)
    profits = w @ profit_data.profits

    mask = (profits < target_return) & (profit_data.max_profit > profits)
    if np.any(mask):
        beta = np.minimum(
            1.0,
            (target_return - profits[mask]) / (profit_data.max_profit - profits[mask]),
        )
        w[mask] *= (1.0 - beta)[:, None]
        w[mask, profit_data.best_idx] += beta
        profits[mask] = w[mask] @ profit_data.profits

    return w, profits


def project_simplex(weights: list[float]) -> list[float]:
    """Project a list vector onto {w >= 0, sum(w) == 1} in Euclidean distance."""
    if not weights:
        raise ValueError("Cannot project an empty weight vector")
    return project_simplex_1d(np.asarray(weights, dtype=np.float64)).tolist()


def repair(
    portfolio: list[Portfolio],
    weights: list[float],
    target_return: float,
) -> list[float]:
    repaired, _ = repair_1d(
        np.asarray(weights, dtype=np.float64),
        get_profit_data(portfolio),
        target_return,
    )
    return repaired.tolist()
# =============================================================================
# END AI-ASSISTED SECTION
# =============================================================================
