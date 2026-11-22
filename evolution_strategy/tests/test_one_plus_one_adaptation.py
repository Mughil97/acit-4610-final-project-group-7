"""Tests for (1+1)-ES strict improvement and per-trial sigma updates.
"""
import math

import numpy as np
import pytest

from evolution_strategy import algorithms
from evolution_strategy.portfolio import (
    Portfolio,
    datafiles,
    read_portfolio_data,
)
from evolution_strategy.evolution_strategies import run_es


def test_success_multiplier_is_exact():
    sigma = 0.1
    assert algorithms.update_one_plus_one_sigma(
        sigma, True
    ) == pytest.approx(sigma * math.exp(1.0 / 3.0))


def test_failure_multiplier_is_exact():
    sigma = 0.1
    assert algorithms.update_one_plus_one_sigma(
        sigma, False
    ) == pytest.approx(sigma * math.exp(-1.0 / 12.0))


def test_sigma_clamps_at_upper_bound():
    assert algorithms.update_one_plus_one_sigma(
        1.0, True
    ) == 1.0


def test_sigma_clamps_at_lower_bound():
    assert algorithms.update_one_plus_one_sigma(
        1e-8, False
    ) == 1e-8


# =============================================================================
# BEGIN AI-ASSISTED SECTION
# Purpose: Adapt (1+1)-ES strict-improvement and per-trial sigma tests to the
#          vectorized _evaluate_candidate_1d and np.random.Generator interface.
# =============================================================================
class _DeterministicRNG:
    def __init__(self, normal_value: float = 0.0):
        self._normal_value = normal_value

    def uniform(self, low, high, size):
        return np.full(size, 0.5, dtype=np.float64)

    def standard_normal(self, size):
        return np.full(size, self._normal_value, dtype=np.float64)


def test_equal_cost_offspring_is_rejected(monkeypatch):
    # Parent and child have equal variance, but different weights.
    responses = iter([
        (0.05, 0.50, np.array([0.2, 0.8], dtype=np.float64)),
        (0.05, 0.50, np.array([0.7, 0.3], dtype=np.float64)),
    ])

    monkeypatch.setattr(
        algorithms,
        "_evaluate_candidate_1d",
        lambda *args: next(responses),
    )

    p = [
        Portfolio(0.02, 0.1, [1.0, 0.0]),
        Portfolio(0.10, 0.2, [0.0, 1.0]),
    ]

    weights, profit, cost, history = algorithms.run_one_plus_one(
        p, target_return=0.02, max_iterations=2, rng=_DeterministicRNG(0.0)
    )

    assert weights == pytest.approx([0.2, 0.8])
    assert profit == 0.05
    assert cost == 0.50
    assert history == [0.50, 0.50]


def test_sigma_is_updated_after_each_trial(monkeypatch):
    # Initial parent, success, equal-cost failure, success.
    costs = iter([10.0, 9.0, 9.0, 8.0])
    observed_steps = []

    def fake_evaluate(weights, profit_data, cov, target):
        cost = next(costs)
        if cost != 10.0:
            # With standard_normal == 1.0 and parent weights == [0.5, 0.5],
            # candidate == [0.5 + sigma, 0.5 + sigma].
            observed_steps.append(float(weights[0] - 0.5))
        return 0.05, cost, np.array([0.5, 0.5], dtype=np.float64)

    monkeypatch.setattr(
        algorithms, "_evaluate_candidate_1d", fake_evaluate
    )

    p = [
        Portfolio(0.02, 0.1, [1.0, 0.0]),
        Portfolio(0.10, 0.2, [0.0, 1.0]),
    ]

    _, _, final_cost, history = algorithms.run_one_plus_one(
        p, target_return=0.02, max_iterations=4, rng=_DeterministicRNG(1.0)
    )

    s0 = 0.1 / math.sqrt(2)
    s1 = s0 * math.exp(1.0 / 3.0)
    s2 = s1 * math.exp(-1.0 / 12.0)

    assert observed_steps == pytest.approx([s0, s1, s2])
    assert history == [10.0, 9.0, 9.0, 8.0]
    assert final_cost == 8.0
# =============================================================================
# END AI-ASSISTED SECTION
# =============================================================================


def test_one_plus_one_runs_with_real_portfolio():
    portfolio = read_portfolio_data(datafiles["port1"])

    result = run_es(
        portfolio,
        alpha=0.5,
        variant="one_plus_one",
        max_iterations=51,
        seed=42,
    )

    assert len(result.history) == 51
    assert result.is_valid
    assert all(
        a >= b
        for a, b in zip(result.history, result.history[1:])
    )
    assert result.cost == pytest.approx(result.history[-1])
