"""Regression tests for Portfolio 2026 Problem 2, simplex projection.

Run from the repository root: python -m pytest -q evolution_strategy/tests/test_repair_projection.py
"""
import math
import random

import numpy as np
import pytest

from evolution_strategy.evaluation import (
    evaluate_batch_cost,
    evaluate_cost,
    evaluate_profit,
    get_covariance_matrix,
    get_profit_data,
    get_target_return,
)
from evolution_strategy.portfolio import Portfolio, datafiles, read_portfolio_data
from evolution_strategy.repair import (
    project_simplex,
    project_simplex_batch,
    repair,
    repair_batch,
)


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


# =============================================================================
# BEGIN AI-ASSISTED SECTION
# Purpose: Verify batch simplex projection, batch return repair, and batch
#          variance evaluation match their scalar counterparts to 1e-12.
# =============================================================================
def test_batch_repair_and_cost_match_scalar():
    p = read_portfolio_data(datafiles["port1"])
    target = get_target_return(p, 0.50)
    rng = np.random.default_rng(123)
    raw = rng.uniform(-1.0, 1.0, size=(12, len(p)))

    proj_batch = project_simplex_batch(raw)
    rep_batch, prof_batch = repair_batch(raw, get_profit_data(p), target)
    cost_batch = evaluate_batch_cost(get_covariance_matrix(p), rep_batch)

    for i in range(raw.shape[0]):
        assert proj_batch[i].tolist() == pytest.approx(
            project_simplex(raw[i].tolist()), abs=1e-12
        )
        rep_scalar = repair(p, raw[i].tolist(), target)
        assert rep_batch[i].tolist() == pytest.approx(rep_scalar, abs=1e-12)
        assert float(prof_batch[i]) == pytest.approx(
            evaluate_profit(p, rep_scalar), abs=1e-12
        )
        assert float(cost_batch[i]) == pytest.approx(
            evaluate_cost(p, rep_scalar), abs=1e-12
        )
# =============================================================================
# END AI-ASSISTED SECTION
# =============================================================================
