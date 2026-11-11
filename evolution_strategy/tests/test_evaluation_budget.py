"""Regression tests for the ES objective-evaluation budget."""

import pytest

from evolution_strategy import algorithms
from evolution_strategy.portfolio import Portfolio


@pytest.mark.parametrize(
    "algorithm_name",
    [
        "run_one_plus_one",
        "run_ten_plus_seventy",
        "run_ten_comma_seventy",
    ],
)
@pytest.mark.parametrize("budget", [83, 30000])
def test_exact_evaluation_budget(monkeypatch, algorithm_name, budget):
    """Count initial and offspring evaluations, including rejected trials."""
    evaluation_count = 0

    def fake_evaluate(portfolio, weights, target_return):
        nonlocal evaluation_count
        evaluation_count += 1

        # Equal costs ensure offspring are not strictly better.
        return 0.05, 0.50, list(weights)

    monkeypatch.setattr(
        algorithms, "evaluate_one_plus_one", fake_evaluate
    )

    portfolio = [
        Portfolio(0.02, 0.1),
        Portfolio(0.10, 0.2),
    ]

    algorithm = getattr(algorithms, algorithm_name)

    weights, profit, cost, history = algorithm(
        portfolio,
        target_return=0.02,
        max_iterations=budget,
    )

    assert evaluation_count == budget
    assert len(history) == budget
