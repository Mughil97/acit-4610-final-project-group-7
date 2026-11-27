"""Regression tests for the separate ES best-so-far record.

Verify initialization, archive updates, rejected offspring,
evaluation accounting, and nonincreasing convergence histories.
"""

import random

import pytest

from evolution_strategy import algorithms
from evolution_strategy.evaluation import get_target_return
from evolution_strategy.results import PORTFOLIOS


def test_one_plus_one_archive_includes_initial_solution(monkeypatch):
    """The initial evaluated portfolio must be archived."""

    weights = [0.4, 0.6]

    def fake_evaluate(portfolio, candidate, target_return):
        return 0.05, 0.01, weights

    monkeypatch.setattr(algorithms, "evaluate_one_plus_one", fake_evaluate)

    best_weights, best_profit, best_cost, history = algorithms.run_one_plus_one(
        [None, None], target_return=0.04, max_iterations=1
    )

    assert best_weights == weights
    assert best_weights is not weights
    assert best_profit == 0.05
    assert best_cost == 0.01
    assert history == [0.01]


def test_one_plus_one_archive_preserves_best_solution(monkeypatch):
    """Worse and equal-cost offspring must not replace the best."""

    evaluations = iter(
        [
            (0.05, 0.04, [0.5, 0.5]),
            (0.06, 0.02, [0.4, 0.6]),
            (0.07, 0.03, [0.3, 0.7]),
            (0.08, 0.02, [0.2, 0.8]),
            (0.09, 0.01, [0.1, 0.9]),
        ]
    )

    def fake_evaluate(portfolio, candidate, target_return):
        return next(evaluations)

    monkeypatch.setattr(algorithms, "evaluate_one_plus_one", fake_evaluate)

    best_weights, best_profit, best_cost, history = algorithms.run_one_plus_one(
        [None, None], target_return=0.04, max_iterations=5
    )

    assert best_weights == [0.1, 0.9]
    assert best_profit == 0.09
    assert best_cost == 0.01

    assert history == [0.04, 0.02, 0.02, 0.02, 0.01]


@pytest.mark.parametrize(
    "variant",
    [
        algorithms.run_one_plus_one,
        algorithms.run_ten_plus_seventy,
        algorithms.run_ten_comma_seventy,
    ],
    ids=["one_plus_one", "plus", "comma"],
)
def test_es_best_so_far_history(variant):
    """All variants must return their recorded best solution."""

    portfolio = PORTFOLIOS["port1"]
    target = get_target_return(portfolio, 0.50)

    random.seed(0)

    weights, profit, cost, history = variant(portfolio, target, max_iterations=500)

    assert len(history) == 500
    assert cost == history[-1]
    assert cost == min(history)

    assert all(
        next_cost <= previous_cost
        for previous_cost, next_cost in zip(history, history[1:])
    )

    assert min(weights) >= -1e-8
    assert abs(sum(weights) - 1.0) <= 1e-8
    assert profit >= target - 1e-8
