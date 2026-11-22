# =============================================================================
# BEGIN AI-ASSISTED SECTION
# Purpose: Cache precomputed profit vectors and covariance matrices per
#          portfolio to vectorize evaluate_profit and evaluate_cost with NumPy.
# =============================================================================
import numpy as np

from evolution_strategy.portfolio import Portfolio

_PROFITS_CACHE: dict[int, tuple[list[Portfolio], np.ndarray]] = {}
_COV_CACHE: dict[int, tuple[list[Portfolio], np.ndarray]] = {}


def _get_profits(portfolio: list[Portfolio]) -> np.ndarray:
    key = id(portfolio)
    cached = _PROFITS_CACHE.get(key)
    if cached is not None and cached[0] is portfolio:
        return cached[1]

    profits = np.array([asset.profit for asset in portfolio], dtype=np.float64)
    if len(_PROFITS_CACHE) >= 32:
        _PROFITS_CACHE.clear()
    _PROFITS_CACHE[key] = (portfolio, profits)
    return profits


def _get_covariance(portfolio: list[Portfolio]) -> np.ndarray:
    key = id(portfolio)
    cached = _COV_CACHE.get(key)
    if cached is not None and cached[0] is portfolio:
        return cached[1]

    risks = np.array([asset.risk for asset in portfolio], dtype=np.float64)
    corr = np.array([asset.correlations for asset in portfolio], dtype=np.float64)
    cov = np.ascontiguousarray(corr * np.outer(risks, risks), dtype=np.float64)
    np.fill_diagonal(cov, risks ** 2)

    if len(_COV_CACHE) >= 32:
        _COV_CACHE.clear()
    _COV_CACHE[key] = (portfolio, cov)
    return cov


def evaluate_profit(portfolio: list[Portfolio], weights: list[float]) -> float:
    return float(np.dot(weights, _get_profits(portfolio)))


def evaluate_cost(portfolio: list[Portfolio], weights: list[float]) -> float:
    w = np.asarray(weights, dtype=np.float64)
    cov = _get_covariance(portfolio)
    return float(w @ (cov @ w))
# =============================================================================
# END AI-ASSISTED SECTION
# =============================================================================


def get_target_return(portfolio: list[Portfolio], alpha: float) -> float:
    profits = [c.profit for c in portfolio]
    r_eq = sum(profits) / len(profits)
    return (1.0 - alpha) * r_eq + alpha * max(profits)
