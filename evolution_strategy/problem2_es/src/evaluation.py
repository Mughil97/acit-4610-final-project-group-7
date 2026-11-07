
from evolution_strategy.problem2_es.src.portfolio import Portfolio


def evaluate_profit(portfolio: list[Portfolio], weights: list[float]) -> float:
    total_profit = 0.0
    for i in range(len(portfolio)):
        total_profit += weights[i] * portfolio[i].profit
    return total_profit


def evaluate_cost(portfolio: list[Portfolio], weights: list[float]) -> float:
    total_risk = 0.0
    n = len(portfolio)

    for i in range(n):
        total_risk += weights[i] ** 2 * portfolio[i].risk ** 2
        for j in range(i + 1, n):
            total_risk += 2 * weights[i] * weights[j] * portfolio[i].risk * portfolio[j].risk * portfolio[i].correlations[j]

    return total_risk


def get_target_return(portfolio: list[Portfolio], alpha: float) -> float:
    profits = [c.profit for c in portfolio]
    r_eq = sum(profits) / len(profits)
    return (1.0 - alpha) * r_eq + alpha * max(profits)

