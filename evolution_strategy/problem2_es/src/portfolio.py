"""OR-Library portfolio parsing, covariance construction and feasibility repair.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import numpy as np

EXPECTED_SIZES = {"port1": 31, "port2": 85, "port3": 89, "port4": 98, "port5": 225}
ALPHAS = (0.25, 0.50, 0.75)
TOLERANCE = 1e-8


@dataclass(frozen=True)
class Portfolio:
    """Validated OR-Library statistics and derived covariance matrix."""
    name: str
    returns: np.ndarray
    stddevs: np.ndarray
    correlation: np.ndarray
    covariance: np.ndarray

    @property
    def n(self) -> int:
        return int(self.returns.size)

    @property
    def equal_return(self) -> float:
        return float(np.mean(self.returns))

    @property
    def max_return(self) -> float:
        return float(np.max(self.returns))

    def target(self, alpha: float) -> float:
        if not 0 <= alpha <= 1:
            raise ValueError("alpha must be in [0, 1]")
        return float((1 - alpha) * self.equal_return + alpha * self.max_return)

    def expected_return(self, weights: np.ndarray) -> float:
        return float(np.dot(self.returns, weights))

    def variance(self, weights: np.ndarray) -> float:
        return float(weights @ self.covariance @ weights)

    def validate(self, weights: np.ndarray, target: float, atol: float = TOLERANCE) -> bool:
        weights = np.asarray(weights, dtype=float)
        return bool(
            weights.shape == (self.n,)
            and np.isfinite(weights).all()
            and np.min(weights) >= -atol
            and abs(float(weights.sum()) - 1.0) <= atol
            and self.expected_return(weights) >= target - atol
        )


def load_portfolio(path: str | Path, *, expected_n: int | None = None) -> Portfolio:
    """Strictly parse n, n lines of (mean,std), and n(n+1)/2 1-based correlations.

    The assignment requires unique and complete upper/lower triangle records.
    """
    path = Path(path)
    records = [line.strip() for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    if not records:
        raise ValueError(f"Empty dataset: {path}")
    first = records[0].split()
    if len(first) != 1:
        raise ValueError(f"First line must contain only n: {path}")
    n = int(first[0])
    inferred = EXPECTED_SIZES.get(path.stem.lower())
    required = expected_n if expected_n is not None else inferred
    if n < 1 or (required is not None and n != required):
        raise ValueError(f"Invalid asset count in {path}: got {n}, expected {required}")
    expected_corr = n * (n + 1) // 2
    if len(records) != 1 + n + expected_corr:
        raise ValueError(f"Bad record count for {path}: expected {1+n+expected_corr}, got {len(records)}")
    returns = np.empty(n, dtype=float)
    stddevs = np.empty(n, dtype=float)
    for i, line in enumerate(records[1:1+n]):
        parts = line.split()
        if len(parts) != 2:
            raise ValueError(f"Expected return and stddev for asset {i+1}")
        returns[i], stddevs[i] = map(float, parts)
    if not np.isfinite(returns).all() or not np.isfinite(stddevs).all() or np.any(stddevs < 0):
        raise ValueError("Non-finite return or invalid standard deviation")
    corr = np.full((n,n), np.nan, dtype=float)
    seen = set()
    for line in records[1+n:]:
        parts = line.split()
        if len(parts) != 3:
            raise ValueError(f"Invalid correlation record: {line!r}")
        i, j = int(parts[0]) - 1, int(parts[1]) - 1
        value = float(parts[2])
        if not 0 <= i < n or not 0 <= j < n:
            raise ValueError(f"Correlation indices out of bounds: {(i+1,j+1)}")
        key = (min(i,j),max(i,j))
        if key in seen:
            raise ValueError(f"Duplicate correlation pair: {(i+1,j+1)}")
        if not np.isfinite(value) or not -1-1e-10 <= value <= 1+1e-10:
            raise ValueError(f"Invalid correlation for pair: {(i+1,j+1)}")
        seen.add(key)
        corr[i,j] = corr[j,i] = value
    if np.isnan(corr).any() or not np.allclose(np.diag(corr),1,rtol=0,atol=1e-8):
        raise ValueError("Missing correlations or diagonal differs from 1")
    covariance = (stddevs[:,None] * corr) * stddevs[None,:]
    return Portfolio(path.stem,returns,stddevs,corr,covariance)


def project_simplex(z: np.ndarray) -> np.ndarray:
    """Euclidean projection onto {w >= 0, sum(w)=1} (not simple clipping)."""
    z = np.asarray(z, dtype=float)
    if z.ndim != 1 or z.size == 0 or not np.isfinite(z).all():
        raise ValueError("Simplex input must be a finite, nonempty vector")
    sorted_z = np.sort(z)[::-1]
    cssv = np.cumsum(sorted_z) - 1.0
    hits = np.nonzero(sorted_z - cssv / np.arange(1,z.size+1) > 0.0)[0]
    rho = int(hits[-1])
    theta = cssv[rho] / (rho+1)
    return np.maximum(z-theta,0.0)


def repair(z: np.ndarray, portfolio: Portfolio, target: float) -> np.ndarray:
    """Repair candidate weights to satisfy budget and return constraints.

    First project onto the probability simplex, then blend toward
    the maximum-return asset when the expected return is too low.
    """
    if target > portfolio.max_return + 1e-10:
        raise ValueError("Return target is greater than highest asset return")
    q = project_simplex(z)
    rq = portfolio.expected_return(q)
    if rq >= target:
        w = q
    else:
        j = int(np.argmax(portfolio.returns))
        denominator = portfolio.max_return - rq
        if denominator <= 0:
            raise ArithmeticError("Cannot repair return with a zero denominator")
        beta = np.clip((target-rq)/denominator,0.0,1.0)
        w = (1.0-beta)*q
        w[j] += beta
    if not portfolio.validate(w,target):
        raise ArithmeticError("Feasibility repair did not satisfy project tolerances")
    return w


def check_port1_checkpoint(portfolio: Portfolio) -> None:
    """Hard validation against the three published port1 numerical checkpoints."""
    if portfolio.name.lower() != "port1" or portfolio.n != 31:
        raise ValueError("Checkpoint is only for the original port1.txt (31 assets)")
    u = np.full(portfolio.n,1.0/portfolio.n)
    checks = {
        "equal allocation return": (portfolio.expected_return(u),0.003504064516129),
        "equal allocation variance": (portfolio.variance(u),0.001130937943724),
        "alpha=0.50 target": (portfolio.target(0.50),0.007184532258065),
    }
    for field,(actual,expected) in checks.items():
        if not np.isclose(actual,expected,rtol=1e-8,atol=1e-12):
            raise ValueError(f"port1 validation failed for {field}: {actual:.15g} != {expected:.15g}")
