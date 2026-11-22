# =============================================================================
# BEGIN AI-ASSISTED SECTION
# Purpose: Precompute and cache per-portfolio profit metadata and symmetric
#          covariance matrices, providing scalar and batch NumPy evaluators.
# =============================================================================
from dataclasses import dataclass
import numpy as np

from evolution_strategy.portfolio import Portfolio


@dataclass(frozen=True)
class ProfitData:
    profits: np.ndarray
    best_idx: int
    max_profit: float


_PROFIT_CACHE: dict[int, tuple[list[Portfolio], ProfitData]] = {}
_COV_CACHE: dict[int, tuple[list[Portfolio], np.ndarray]] = {}


def get_profit_data(portfolio: list[Portfolio]) -> ProfitData:
    key = id(portfolio)
    cached = _PROFIT_CACHE.get(key)
    if cached is not None and cached[0] is portfolio:
        return cached[1]

    profits = np.array([asset.profit for asset in portfolio], dtype=np.float64)
    best_idx = int(np.argmax(profits))
    data = ProfitData(
        profits=profits,
        best_idx=best_idx,
        max_profit=float(profits[best_idx]),
    )
    if len(_PROFIT_CACHE) >= 32:
        _PROFIT_CACHE.clear()
    _PROFIT_CACHE[key] = (portfolio, data)
    return data


def get_covariance_matrix(portfolio: list[Portfolio]) -> np.ndarray:
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
    return float(np.dot(weights, get_profit_data(portfolio).profits))


def evaluate_cost(portfolio: list[Portfolio], weights: list[float]) -> float:
    w = np.asarray(weights, dtype=np.float64)
    cov = get_covariance_matrix(portfolio)
    return float(w @ (cov @ w))


def evaluate_batch_cost(cov: np.ndarray, weights_batch: np.ndarray) -> np.ndarray:
    """Compute portfolio variances for a (batch_size, n) matrix via BLAS DGEMM."""
    return np.einsum("ij,ij->i", weights_batch @ cov, weights_batch)


def get_target_return(portfolio: list[Portfolio], alpha: float) -> float:
    data = get_profit_data(portfolio)
    r_eq = float(np.mean(data.profits))
    return (1.0 - alpha) * r_eq + alpha * data.max_profit
# =============================================================================
# END AI-ASSISTED SECTION
# =============================================================================
