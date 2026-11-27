"""Evolution Strategy algorithms for portfolio optimization.

Implements the three variants required by Portfolio 2026,
Problem 2, pages 10-11:

1. (1+1)-ES:
   One parent and one offspring, using a scalar mutation
   step size adapted through the 1/5 success rule.

2. (10+70)-ES:
   Population-based elitist Evolution Strategy.
   Parents and offspring compete for survival.

3. (10,70)-ES:
   Population-based non-elitist Evolution Strategy.
   Only offspring compete for survival.

All variants minimize portfolio variance, repair candidate
weights before evaluation, and record the best solution found
within the objective evaluation budget.
"""

from dataclasses import dataclass
import math
import random

from evolution_strategy.repair import repair
from evolution_strategy.evaluation import evaluate_cost, evaluate_profit
from evolution_strategy.portfolio import Portfolio


@dataclass
class Individual:
    """Represent one candidate portfolio in population-based ES.

    Attributes:
        weights:
            Portfolio decision variables. Each weight represents
            the fraction of capital allocated to an asset.

        sigmas:
            Mutation step sizes associated with individual
            decision variables. These evolve together with
            the portfolio weights.

        profit:
            Expected portfolio return.

        cost:
            Portfolio variance. Lower values are preferred.

    The weights represent the solution, while sigmas are
    strategy parameters controlling the mutation process.
    """

    weights: list[float]
    sigmas: list[float]
    profit: float
    cost: float


def evaluate_one_plus_one(
    portfolio: list[Portfolio], weights: list[float], target_return: float
):
    """Repair and evaluate a candidate portfolio.

    Despite its name, this helper is shared by all three
    Evolution Strategy variants.

    Evaluation sequence:
        1. Repair the candidate weights.
        2. Calculate the expected portfolio return.
        3. Calculate the portfolio variance.
        4. Return the evaluation results and repaired weights.

    Each call represents one candidate objective evaluation.
    """
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

    Accept only strictly lower-variance offspring and update sigma
    after each evaluated child using the 1/5 success rule.

    Maintain a separate best-so-far record, including the initial
    repaired portfolio, as required by Portfolio 2026, Problem 2.
    """
    n = len(portfolio)
    if sigma is None:
        sigma = 0.1 / math.sqrt(n)
    sigma = max(1e-8, min(1.0, sigma))

    current_weights = [random.uniform(0.0, 1.0) for _ in range(n)]
    current_profit, current_cost, current_weights = evaluate_one_plus_one(
        portfolio, current_weights, target_return
    )
    # correction: separate best-so-far archive.
    # Include the initial repaired portfolio.
    best_weights = current_weights.copy()
    best_profit = current_profit
    best_cost = current_cost

    history = [best_cost]

    for _ in range(1, max_iterations):
        # Gaussian mutation:
        # w'_i = w_i + sigma * N_i(0, 1)
        #
        # Each coordinate receives independent Gaussian noise,
        # but all coordinates share the same scalar sigma.
        new_weights = [weight + random.gauss(0, sigma) for weight in current_weights]
        new_profit, new_cost, repaired_weights = evaluate_one_plus_one(
            portfolio, new_weights, target_return
        )

        improved = new_cost < current_cost  # strict improvement only

        if improved:
            current_weights = repaired_weights
            current_profit = new_profit
            current_cost = new_cost

        # AI Assisted
        # Update the separate best-so-far archive.
        if new_cost < best_cost:
            best_weights = repaired_weights.copy()
            best_profit = new_profit
            best_cost = new_cost
        # End AI Assisted

        history.append(best_cost)

        # Adapt the mutation step size after every trial.
        # Successful mutation increases sigma, while an
        # unsuccessful mutation decreases sigma.
        sigma = update_one_plus_one_sigma(sigma, improved)

    return best_weights, best_profit, best_cost, history


# (10+70)-ES Algorithm
def run_ten_plus_seventy(
    portfolio: list[Portfolio],
    target_return: float,
    max_iterations: int = 30000,
    mu: int = 10,
    lambda_: int = 70,
):
    """Run the elitist (mu + lambda) Evolution Strategy.

    Assignment configuration:
        mu = 10 parents
        lambda = 70 offspring

    The plus strategy is elitist because existing parents
    can survive into the next generation.

    A separate best-so-far record preserves the best
    evaluated solution throughout the search.
    """
    n = len(portfolio)
    # Initial mutation step size for each coordinate.
    init_sigma = 0.1 / math.sqrt(n)
    # Global and coordinate-specific learning rates.
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
        profit, cost, weights = evaluate_one_plus_one(
            portfolio, raw_weights, target_return
        )
        sigmas = [init_sigma] * n
        population.append(Individual(weights, sigmas, profit, cost))
        if cost < best_cost:
            best_weights, best_profit, best_cost = weights, profit, cost
        history.append(best_cost)

    evaluations = mu

    while evaluations < max_iterations:
        # Prevent exceeding the objective evaluation budget.
        batch_size = min(lambda_, max_iterations - evaluations)
        offspring: list[Individual] = []

        for _ in range(batch_size):
            # 1. Select 2 parents at random
            parent1, parent2 = random.sample(population, 2)

            # 2. Arithmetic recombination of weights and
            # geometric recombination of mutation step sizes.
            child_weights = [
                (parent1.weights[i] + parent2.weights[i]) / 2.0 for i in range(n)
            ]
            child_sigmas = [
                math.sqrt(parent1.sigmas[i] * parent2.sigmas[i]) for i in range(n)
            ]

            # 3. Log-normal self-adaptation of sigmas,
            # followed by Gaussian mutation of weights.
            # z0 is shared across all coordinates.
            z0 = random.gauss(0, 1)
            for i in range(n):
                child_sigmas[i] *= math.exp(tau_prime * z0 + tau * random.gauss(0, 1))
                child_sigmas[i] = max(1e-8, min(1.0, child_sigmas[i]))
                child_weights[i] += child_sigmas[i] * random.gauss(0, 1)

            # 4. Evaluate offspring
            profit, cost, child_weights = evaluate_one_plus_one(
                portfolio, child_weights, target_return
            )
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
    """Run the non-elitist (mu, lambda) Evolution Strategy.

    Assignment configuration:
        mu = 10 parents
        lambda = 70 offspring

    Initialization, recombination, mutation and repair are
    shared in principle with the plus strategy.

    The main difference is survivor selection:

        Only the offspring population is eligible for
        selection into the next parent population.

    The previous parents are discarded after a complete
    offspring batch, even when they have lower variance.

    This can promote exploration but may also lose previously
    discovered high-quality solutions.

    A separate best-so-far record preserves the best solution
    for reporting. It does not participate in parent selection
    or survivor selection.

    An incomplete final offspring batch is still evaluated
    and included in the best-so-far record.
    """
    n = len(portfolio)
    # Initial mutation step size for each coordinate:
    # sigma_0 = 0.1 / sqrt(n)
    init_sigma = 0.1 / math.sqrt(n)

    # tau_prime: global learning rate controlling a shared
    # adjustment across all coordinates.
    tau_prime = 1.0 / math.sqrt(2.0 * n)

    # tau: coordinate-specific learning rate controlling
    # independent adjustments to individual step sizes.
    tau = 1.0 / math.sqrt(2.0 * math.sqrt(n))

    # Initialize population of mu individuals: (weights, sigmas, profit, cost)
    population: list[Individual] = []
    history: list[float] = []
    best_weights: list[float] = []
    best_profit = 0.0
    best_cost = float("inf")

    for _ in range(mu):
        raw_weights = [random.uniform(0.0, 1.0) for _ in range(n)]
        profit, cost, weights = evaluate_one_plus_one(
            portfolio, raw_weights, target_return
        )
        sigmas = [init_sigma] * n
        population.append(Individual(weights, sigmas, profit, cost))
        if cost < best_cost:
            best_weights, best_profit, best_cost = weights, profit, cost
        history.append(best_cost)

    evaluations = mu

    while evaluations < max_iterations:
        # Limit offspring production to the remaining evaluation
        # budget. The final generation may therefore be incomplete.
        # This prevents exceeding 30,000 objective evaluations.
        batch_size = min(lambda_, max_iterations - evaluations)
        offspring: list[Individual] = []

        for _ in range(batch_size):
            # 1. Select 2 parents at random
            parent1, parent2 = random.sample(population, 2)

            # 2. Arithmetic recombination of weights and
            # geometric recombination of mutation step sizes.
            child_weights = [
                (parent1.weights[i] + parent2.weights[i]) / 2.0 for i in range(n)
            ]
            child_sigmas = [
                math.sqrt(parent1.sigmas[i] * parent2.sigmas[i]) for i in range(n)
            ]

            # 3. Mutate sigmas (self-adaptation) and weights
            # Log-normal self-adaptation:
            #
            # sigma'_i = sigma_i * exp(tau_prime * z0 + tau * zi)
            #
            # z0 is shared across the child's coordinates.
            # zi is independently sampled for each coordinate.
            #
            # Update sigma first, then use the updated sigma
            # to mutate the corresponding portfolio weight.
            z0 = random.gauss(0, 1)
            for i in range(n):
                child_sigmas[i] *= math.exp(tau_prime * z0 + tau * random.gauss(0, 1))
                child_sigmas[i] = max(1e-8, min(1.0, child_sigmas[i]))
                child_weights[i] += child_sigmas[i] * random.gauss(0, 1)

            # 4. Evaluate offspring
            profit, cost, child_weights = evaluate_one_plus_one(
                portfolio, child_weights, target_return
            )
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
