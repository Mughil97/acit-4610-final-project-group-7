from dataclasses import dataclass
import math
import random

from evolution_strategy.repair import repair
from evolution_strategy.evaluation import (
    evaluate_cost, 
    evaluate_profit
)
from evolution_strategy.portfolio import Portfolio


@dataclass
class Individual:
    weights: list[float]
    sigmas: list[float]
    profit: float
    cost: float


def evaluate_one_plus_one(
        portfolio: list[Portfolio],
        weights: list[float],
        target_return: float
):
    repaired_weights = repair(portfolio, weights, target_return)
    profit = evaluate_profit(portfolio, repaired_weights)
    cost = evaluate_cost(portfolio, repaired_weights)
    return profit, cost, repaired_weights

def update_one_plus_one_sigma(sigma: float, improved: bool) -> float:
    """Apply the assignment's per-trial 1/5-success-rule update.

    The step size is increased after a strictly better child and decreased
    otherwise, with the specified bounds [1e-8, 1.0].
    """
    factor = math.exp(1.0 / 3.0) if improved else math.exp(-1.0 / 12.0)
    return max(1e-8, min(1.0, sigma * factor))

def run_one_plus_one(
        portfolio: list[Portfolio],
        target_return: float,
        max_iterations: int = 30000,
        sigma: float | None = None,
):
    """Run (1+1)-ES, counting initialization as one evaluation.

    In accordance with Portfolio 2026, Problem 2, p. 10, accept only strictly
    lower-variance offspring and update sigma after EACH evaluated child.
    """
    n = len(portfolio)
    if sigma is None:
        sigma = 0.1 / math.sqrt(n)
    sigma = max(1e-8, min(1.0, sigma))

    current_weights = [random.uniform(0.0, 1.0) for _ in range(n)]
    current_profit, current_cost, current_weights = evaluate_one_plus_one(
        portfolio, current_weights, target_return
    )
    history = [current_cost]

    for _ in range(1, max_iterations):
        new_weights = [weight + random.gauss(0, sigma) for weight in current_weights]
        new_profit, new_cost, repaired_weights = evaluate_one_plus_one(
            portfolio, new_weights, target_return
        )

        improved = new_cost < current_cost  # strict improvement only
        if improved:
            current_weights = repaired_weights
            current_profit = new_profit
            current_cost = new_cost

        history.append(current_cost)
        sigma = update_one_plus_one_sigma(sigma, improved)

    return current_weights, current_profit, current_cost, history

# (10+70)-ES Algorithm
def run_ten_plus_seventy(
        portfolio: list[Portfolio],
        target_return: float,
        max_iterations: int = 30000,
        mu: int = 10,
        lambda_: int = 70,
):
    n = len(portfolio)
    init_sigma = 0.1 / math.sqrt(n)
    tau_prime = 1.0 / math.sqrt(2.0 * n)
    tau = 1.0 / math.sqrt(2.0 * math.sqrt(n))

    # Initialize population of mu individuals: (weights, sigmas, profit, cost)
    population: list[Individual] = []
    history: list[float] = []
    best_weights: list[float] = []
    best_profit = 0.0
    best_cost = float("inf")

    for _ in range(mu):
        raw_weights = [random.uniform(0.0, 1.0) for _ in range(n)]
        profit, cost, weights = evaluate_one_plus_one(portfolio, raw_weights, target_return)
        sigmas = [init_sigma] * n
        population.append(Individual(weights, sigmas, profit, cost))
        if cost < best_cost:
            best_weights, best_profit, best_cost = weights, profit, cost
        history.append(best_cost)

    evaluations = mu

    while evaluations < max_iterations:
        batch_size = min(lambda_, max_iterations - evaluations)
        offspring: list[Individual] = []

        for _ in range(batch_size):
            # 1. Select 2 parents at random
            parent1, parent2 = random.sample(population, 2)

            # 2. Recombine weights and sigmas
            child_weights = [(parent1.weights[i] + parent2.weights[i]) / 2.0 for i in range(n)]
            child_sigmas = [math.sqrt(parent1.sigmas[i] * parent2.sigmas[i]) for i in range(n)]

            # 3. Mutate sigmas (self-adaptation) and weights
            z0 = random.gauss(0, 1)
            for i in range(n):
                child_sigmas[i] *= math.exp(tau_prime * z0 + tau * random.gauss(0, 1))
                child_sigmas[i] = max(1e-8, min(1.0, child_sigmas[i]))
                child_weights[i] += child_sigmas[i] * random.gauss(0, 1)

            # 4. Evaluate offspring
            profit, cost, child_weights = evaluate_one_plus_one(portfolio, child_weights, target_return)
            offspring.append(Individual(child_weights, child_sigmas, profit, cost))

            if cost < best_cost:
                best_weights, best_profit, best_cost = child_weights, profit, cost
            history.append(best_cost)

        evaluations += batch_size

        # (mu + lambda) selection: best mu from parents + offspring
        combined = population + offspring
        combined.sort(key=lambda individual: individual.cost)
        population = combined[:mu]

    return best_weights, best_profit, best_cost, history


# (10,70)-ES Algorithm
def run_ten_comma_seventy(
        portfolio: list[Portfolio],
        target_return: float,
        max_iterations: int = 30000,
        mu: int = 10,
        lambda_: int = 70,
):
    n = len(portfolio)
    init_sigma = 0.1 / math.sqrt(n)
    tau_prime = 1.0 / math.sqrt(2.0 * n)
    tau = 1.0 / math.sqrt(2.0 * math.sqrt(n))

    # Initialize population of mu individuals: (weights, sigmas, profit, cost)
    population: list[Individual] = []
    history: list[float] = []
    best_weights: list[float] = []
    best_profit = 0.0
    best_cost = float("inf")

    for _ in range(mu):
        raw_weights = [random.uniform(0.0, 1.0) for _ in range(n)]
        profit, cost, weights = evaluate_one_plus_one(portfolio, raw_weights, target_return)
        sigmas = [init_sigma] * n
        population.append(Individual(weights, sigmas, profit, cost))
        if cost < best_cost:
            best_weights, best_profit, best_cost = weights, profit, cost
        history.append(best_cost)

    evaluations = mu

    while evaluations < max_iterations:
        batch_size = min(lambda_, max_iterations - evaluations)
        offspring: list[Individual] = []

        for _ in range(batch_size):
            # 1. Select 2 parents at random
            parent1, parent2 = random.sample(population, 2)

            # 2. Recombine weights and sigmas
            child_weights = [(parent1.weights[i] + parent2.weights[i]) / 2.0 for i in range(n)]
            child_sigmas = [math.sqrt(parent1.sigmas[i] * parent2.sigmas[i]) for i in range(n)]

            # 3. Mutate sigmas (self-adaptation) and weights
            z0 = random.gauss(0, 1)
            for i in range(n):
                child_sigmas[i] *= math.exp(tau_prime * z0 + tau * random.gauss(0, 1))
                child_sigmas[i] = max(1e-8, min(1.0, child_sigmas[i]))
                child_weights[i] += child_sigmas[i] * random.gauss(0, 1)

            # 4. Evaluate offspring
            profit, cost, child_weights = evaluate_one_plus_one(portfolio, child_weights, target_return)
            offspring.append(Individual(child_weights, child_sigmas, profit, cost))

            if cost < best_cost:
                best_weights, best_profit, best_cost = child_weights, profit, cost
            history.append(best_cost)

        evaluations += batch_size

        # (mu, lambda) selection: best mu from offspring ONLY
        if len(offspring) >= mu:
            offspring.sort(key=lambda individual: individual.cost)
            population = offspring[:mu]

    return best_weights, best_profit, best_cost, history
