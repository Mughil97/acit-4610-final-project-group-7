
"""Regression tests for Portfolio 2026 Problem 2, simplex projection.

Run from the repository root: python -m pytest -q evolution_strategy/tests/test_repair_projection.py
"""
import math
import random

import pytest

from evolution_strategy.evaluation import evaluate_profit, get_target_return
from evolution_strategy.portfolio import Portfolio, datafiles, read_portfolio_data
from evolution_strategy.repair import project_simplex, repair


def test_projection_differs_from_clipping_and_normalizing():
    assert project_simplex([0.8, 0.3, -0.2]) == pytest.approx(
        [0.75, 0.25, 0.0]
    )


def test_projection_on_the_simplex_is_unchanged():
    assert project_simplex([0.1, 0.4, 0.5]) == pytest.approx(
        [0.1, 0.4, 0.5]
    )


def test_zero_vector_projects_to_uniform_allocation():
    assert project_simplex([0.0] * 4) == pytest.approx([0.25] * 4)


def test_all_negative_vector_can_be_projected():
    assert project_simplex([-3.0, -2.0, -1.0]) == pytest.approx(
        [0.0, 0.0, 1.0]
    )


@pytest.mark.parametrize("n", [31, 85, 89, 98, 225])
def test_projection_feasible_at_portfolio_dimensions(n):
    rng = random.Random(n)
    raw = [rng.uniform(-2.0, 2.0) for _ in range(n)]
    original = raw.copy()

    output = project_simplex(raw)

    assert len(output) == n
    assert min(output) >= 0
    assert math.fsum(output) == pytest.approx(1.0, abs=1e-12)
    assert raw == original

    shifts = [
        z - q for z, q in zip(raw, output)
        if q > 1e-12
    ]
    assert shifts
    assert max(shifts) - min(shifts) <= 1e-12


def test_return_target_repair_preserved():
    p = [
        Portfolio(0.02, 0.1, [1.0, 0.0]),
        Portfolio(0.20, 0.2, [0.0, 1.0])
    ]

    repaired = repair(p, [0.8, 0.2], 0.15)

    assert min(repaired) >= -1e-8
    assert sum(repaired) == pytest.approx(1.0, abs=1e-8)
    assert evaluate_profit(p, repaired) >= 0.15 - 1e-8


@pytest.mark.parametrize("alpha", [0.25, 0.50, 0.75])
def test_full_repair_meets_official_constraints_port1(alpha):
    p = read_portfolio_data(datafiles["port1"])
    target = get_target_return(p, alpha)

    raw = [-0.7, 0.5, 0.9] + [0.01] * (len(p) - 3)
    w = repair(p, raw, target)

    assert len(w) == len(p)
    assert min(w) >= -1e-8
    assert sum(w) == pytest.approx(1.0, abs=1e-8)
    assert evaluate_profit(p, w) >= target - 1e-8


def test_nonfinite_projection_rejected():
    with pytest.raises(ValueError):
        project_simplex([0.5, float("nan"), 0.5])


def test_empty_projection_rejected():
    with pytest.raises(ValueError):
        project_simplex([])
