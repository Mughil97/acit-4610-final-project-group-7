
from evolution_strategy.portfolio import Portfolio
from evolution_strategy.evaluation import evaluate_profit

def repair(portfolio: list[Portfolio], weights: list[float], target_return: float) -> list[float]:
    n = len(portfolio)

    # 1. Clip negative weights and normalize to sum to 1
    weights = [max(0.0, w) for w in weights]
    total = sum(weights)
    if total == 0:
        weights = [1.0 / n] * n
    else:
        weights = [w / total for w in weights]

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