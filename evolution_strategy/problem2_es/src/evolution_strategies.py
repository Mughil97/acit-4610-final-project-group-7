"""Evolution Strategies for constrained portfolio optimization.

Implements (1+1)-ES, (10+70)-ES, and (10,70)-ES using
Gaussian mutation, strategy-parameter adaptation, and
a shared best-so-far solution archive.
"""
# Algorithmic references: ACIT4610 Lecture 2, Lab 2,
# and Portfolio 2026, Problem 2.

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
import numpy as np

from .portfolio import Portfolio, repair

MU, LAMBDA = 10, 70
SIGMA_MIN, SIGMA_MAX = 1e-8, 1.0
VARIANTS = ("one_plus_one", "mu_plus_lambda", "mu_comma_lambda")

@dataclass
class Individual:
    weights: np.ndarray
    sigma: np.ndarray | float
    variance: float


@dataclass
class ESResult:
    variant: str
    seed: int
    budget: int
    evals: int
    initial_best: float
    best_variance: float
    best_weights: np.ndarray
    best_return: float
    best_history: np.ndarray
    runtime_seconds: float
    feasible: bool
    final_population_best: float


class _BudgetedEvaluator:
    """One variance evaluation per candidate; no reevaluation of survivors."""
    def __init__(self, portfolio: Portfolio, target: float, budget: int):
        self.portfolio = portfolio
        self.target = target
        self.budget = budget
        self.evals = 0
        self.history = np.empty(budget,dtype=float)
        self.best_variance = float("inf")
        self.best_weights = None

    def evaluate(self, z: np.ndarray, sigma: np.ndarray | float) -> Individual:
        if self.evals >= self.budget:
            raise RuntimeError("Objective evaluation budget exceeded")
        weights = repair(z,self.portfolio,self.target)
        var = self.portfolio.variance(weights)
        if not np.isfinite(var):
            raise ArithmeticError("Non-finite variance")
        self.evals += 1
        if var < self.best_variance:
            self.best_variance = var
            self.best_weights = weights.copy()
        self.history[self.evals-1] = self.best_variance
        return Individual(weights,sigma,var)


def _one_plus_one(ev: _BudgetedEvaluator, rng: np.random.Generator) -> tuple[float, Individual]:
    n = ev.portfolio.n
    step = 0.1/np.sqrt(n)
    parent = ev.evaluate(rng.uniform(0,1,size=n),step)
    initial = parent.variance
    while ev.evals < ev.budget:
        child = ev.evaluate(parent.weights + step*rng.standard_normal(n),step)
        if child.variance < parent.variance:
            parent = child
            step = min(SIGMA_MAX, step * np.exp(1.0/3.0))
        else:
            step = max(SIGMA_MIN, step * np.exp(-1.0/12.0))
    return initial,parent


def _population_es(ev: _BudgetedEvaluator, rng: np.random.Generator, *, elitist: bool) -> tuple[float,list[Individual]]:
    n = ev.portfolio.n
    if ev.budget < MU:
        raise ValueError(f"Population ES budget must be >= {MU}")
    start_sigma = np.full(n,0.1/np.sqrt(n))
    parents = [ev.evaluate(rng.uniform(0,1,size=n),start_sigma.copy()) for _ in range(MU)]
    initial = min(ind.variance for ind in parents)
    tau_prime = 1.0/np.sqrt(2.0*n)
    tau = 1.0/np.sqrt(2.0*np.sqrt(n))
    while ev.evals < ev.budget:
        offspring: list[Individual] = []
        n_children = min(LAMBDA, ev.budget-ev.evals)
        for _ in range(n_children):
            # Uniform random parent sampling, not fitness-weighted selection.
            i,j = rng.choice(len(parents),size=2,replace=False)
            a,b = parents[int(i)],parents[int(j)]
            weights_recombined = 0.5*(a.weights+b.weights)
            sigma_recombined = np.sqrt(a.sigma*b.sigma)
            z0 = rng.standard_normal()
            zi = rng.standard_normal(n)
            child_sigma = np.clip(
                sigma_recombined * np.exp(tau_prime*z0 + tau*zi),
                SIGMA_MIN,SIGMA_MAX
            )
            # Independent new Gaussian draws after strategy-parameter adaptation.
            raw_weights = weights_recombined + child_sigma*rng.standard_normal(n)
            offspring.append(ev.evaluate(raw_weights,child_sigma))
        if len(offspring) < MU and not elitist:
            # The budget is reached. A comma generation with fewer than mu
            # offspring cannot form a new parent population; archive is still updated.
            break
        candidates = parents+offspring if elitist else offspring
        parents = sorted(candidates,key=lambda ind:ind.variance)[:MU]
    return initial,parents


def run_es(portfolio: Portfolio, alpha: float, variant: str, *, seed: int, budget: int=30_000) -> ESResult:
    """Run one independent trial with an exact number of objective evaluations."""
    if variant not in VARIANTS:
        raise ValueError(f"Variant must be one of {VARIANTS}")
    if budget < (1 if variant=="one_plus_one" else MU):
        raise ValueError("Budget is too small to initialize the parent population")
    target = portfolio.target(alpha)
    rng = np.random.default_rng(seed)
    start = perf_counter()
    ev = _BudgetedEvaluator(portfolio,target,budget)
    if variant == "one_plus_one":
        initial, parent = _one_plus_one(ev,rng)
        final_pop = parent.variance
    else:
        initial, parents = _population_es(ev,rng,elitist=(variant=="mu_plus_lambda"))
        final_pop = min(p.variance for p in parents)
    elapsed = perf_counter()-start
    assert ev.evals == budget, "Exact objective-budget invariant broken"
    assert ev.best_weights is not None
    return ESResult(
        variant=variant, seed=seed, budget=budget, evals=ev.evals,
        initial_best=float(initial), best_variance=ev.best_variance,
        best_weights=ev.best_weights.copy(),
        best_return=portfolio.expected_return(ev.best_weights),
        best_history=ev.history.copy(),runtime_seconds=elapsed,
        feasible=portfolio.validate(ev.best_weights,target),
        final_population_best=float(final_pop)
    )
