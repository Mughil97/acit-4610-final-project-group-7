"""Objective and return calculations for portfolio optimization.

This module implements the mathematical formulation specified
in Portfolio 2026, Problem 2, page 9.

The optimization objective is to minimize portfolio variance
while satisfying the minimum expected-return requirement.
"""

import numpy as np

from evolution_strategy.portfolio import Portfolio, construct_covariance_matrix

# AI Assisted Optimisation
_PROFITS_CACHE: dict[int, tuple[list[Portfolio], np.ndarray]] = {}
_COV_CACHE: dict[int, tuple[list[Portfolio], np.ndarray]] = {}


def _get_profits(portfolio: list[Portfolio]) -> np.ndarray:
    """Return a cached NumPy vector of asset expected returns."""
    key = id(portfolio)
    cached = _PROFITS_CACHE.get(key)
    if cached is not None and cached[0] is portfolio:
        return cached[1]

    profits = np.array(
        [asset.profit for asset in portfolio],
        dtype=np.float64,
    )

    # Bound cache size for temporary test portfolios.
    if len(_PROFITS_CACHE) >= 32:
        _PROFITS_CACHE.clear()
    _PROFITS_CACHE[key] = (portfolio, profits)
    return profits


def _get_covariance(portfolio: list[Portfolio]) -> np.ndarray:
    """Return a cached contiguous NumPy covariance matrix."""
    key = id(portfolio)
    cached = _COV_CACHE.get(key)
    if cached is not None and cached[0] is portfolio:
        return cached[1]

    n = len(portfolio)

    # Reuse the covariance matrix constructed during data loading.
    # The fallback supports manually constructed test portfolios.
    if all(len(asset.covariances) == n for asset in portfolio):
        covariance = [asset.covariances for asset in portfolio]
    else:
        covariance = construct_covariance_matrix(portfolio)

    cov_matrix = np.ascontiguousarray(covariance, dtype=np.float64)

    # Bound cache size for temporary test portfolios.
    if len(_COV_CACHE) >= 32:
        _COV_CACHE.clear()
    _COV_CACHE[key] = (portfolio, cov_matrix)
    return cov_matrix
# End AI Assisted Optimisation


def evaluate_profit(portfolio: list[Portfolio], weights: list[float]) -> float:
    """Calculate the expected return of a portfolio.

    Mathematical formula:
        R(w) = sum(r_i * w_i)

    where:
        r_i = expected return of asset i
        w_i = proportion invested in asset i

    Returns are expressed as decimals, not percentages.
    """
    # AI Assisted Optimisation
    # Compute the dot product r^T w using the cached return vector.
    return float(np.dot(weights, _get_profits(portfolio)))
    # End AI Assisted Optimisation


def evaluate_cost(portfolio: list[Portfolio], weights: list[float]) -> float:
    """Calculate portfolio variance, which ES minimizes.

    Assignment formula:
        V(w) = w^T Sigma w

    The diagonal represents individual asset variances.
    Off-diagonal values represent covariance between assets.
    """
    # AI Assisted Optimisation
    # Evaluate the quadratic form w^T Sigma w using the cached
    # covariance matrix in NumPy instead of nested Python loops.
    w = np.asarray(weights, dtype=np.float64)
    covariance = _get_covariance(portfolio)

    # Return portfolio variance, not standard deviation.
    # Lower variance indicates lower portfolio risk.
    return float(w @ (covariance @ w))
    # End AI Assisted Optimisation


def get_target_return(portfolio: list[Portfolio], alpha: float) -> float:
    """Calculate the required minimum portfolio return.

    Assignment formula:
        R_min = (1 - alpha) * R_eq + alpha * R_max

    where:
        R_eq  = expected return of an equal-weight portfolio
        R_max = highest individual asset expected return
        alpha = required return-level parameter

    The assignment uses alpha values 0.25, 0.50 and 0.75.
    """
    profits = [c.profit for c in portfolio]

    # Equal allocation means that every asset receives 1/n
    # of the total investment budget.
    r_eq = sum(profits) / len(profits)

    # Interpolate between the equal-weight return and
    # the highest individual asset return.
    return (1.0 - alpha) * r_eq + alpha * max(profits)
