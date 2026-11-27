"""Objective and return calculations for portfolio optimization.

This module implements the mathematical formulation specified
in Portfolio 2026, Problem 2, page 9.

The optimization objective is to minimize portfolio variance
while satisfying the minimum expected-return requirement.
"""

from evolution_strategy.portfolio import (
    Portfolio,
    construct_covariance_matrix,
)

def evaluate_profit(portfolio: list[Portfolio], weights: list[float]) -> float:
    """Calculate the expected return of a portfolio.

    Mathematical formula:
        R(w) = sum(r_i * w_i)

    where:
        r_i = expected return of asset i
        w_i = proportion invested in asset i

    Returns are expressed as decimals, not percentages.
    """
    total_profit = 0.0

    # Each asset contributes its expected return
    # multiplied by its allocated portfolio weight.
    for i in range(len(portfolio)):
        total_profit += weights[i] * portfolio[i].profit
    return total_profit


def evaluate_cost(portfolio: list[Portfolio], weights: list[float]) -> float:
    """Calculate portfolio variance, which ES minimizes.

    Assignment formula:
        V(w) = w^T Sigma w

    Expanded formula for a symmetric covariance matrix:
        V(w) = sum(w_i^2 * Sigma_ii)
             + 2 * sum(w_i * w_j * Sigma_ij), for i < j

    The diagonal represents individual asset variances.
    Off-diagonal values represent covariance between assets.

    The upper triangle is evaluated to avoid calculating
    symmetric covariance contributions twice.
    """

    total_risk = 0.0
    n = len(portfolio)

    # Reuse the covariance matrix constructed during data loading.
    # The fallback supports manually constructed test portfolios.
    if all(len(asset.covariances) == n for asset in portfolio):
        covariance = [asset.covariances for asset in portfolio]
    else:
        covariance = construct_covariance_matrix(portfolio)

    for i in range(n):
        # Diagonal contribution:
        # weight squared multiplied by individual asset variance.
        total_risk += weights[i] ** 2 * covariance[i][i]

        for j in range(i + 1, n):
            # Off-diagonal contribution:
            # multiply by 2 because the covariance matrix
            # is symmetric: Sigma[i][j] = Sigma[j][i].
            total_risk += 2 * weights[i] * weights[j] * covariance[i][j]

    # Return portfolio variance, not standard deviation.
    # Lower variance indicates lower portfolio risk.
    return total_risk


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

