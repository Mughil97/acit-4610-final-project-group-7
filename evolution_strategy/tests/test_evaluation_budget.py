"""Regression tests for the ES objective-evaluation budget."""

# =============================================================================
# BEGIN AI-ASSISTED SECTION
# Purpose: Update budget-counting mocks for vectorized 1D and batch ES
#          evaluators in algorithms.py.
# =============================================================================
import numpy as np
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

    def fake_evaluate_1d(weights, profit_data, cov, target_return):
        nonlocal evaluation_count
        evaluation_count += 1
        return 0.05, 0.50, np.array(weights, dtype=np.float64, copy=True)

    def fake_evaluate_batch(weights_batch, profit_data, cov, target_return):
        nonlocal evaluation_count
        bs = weights_batch.shape[0]
        evaluation_count += bs
        return (
            np.full(bs, 0.05, dtype=np.float64),
            np.full(bs, 0.50, dtype=np.float64),
            np.array(weights_batch, dtype=np.float64, copy=True),
        )

    monkeypatch.setattr(
        algorithms, "_evaluate_candidate_1d", fake_evaluate_1d
    )
    monkeypatch.setattr(
        algorithms, "_evaluate_candidates_batch", fake_evaluate_batch
    )

    portfolio = [
        Portfolio(0.02, 0.1, [1.0, 0.0]),
        Portfolio(0.10, 0.2, [0.0, 1.0]),
    ]

    algorithm = getattr(algorithms, algorithm_name)

    weights, profit, cost, history = algorithm(
        portfolio,
        target_return=0.02,
        max_iterations=budget,
    )

    assert evaluation_count == budget
    assert len(history) == budget
# =============================================================================
# END AI-ASSISTED SECTION
# =============================================================================
