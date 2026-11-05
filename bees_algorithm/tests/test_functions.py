import math

import pytest

from bees_algorithm.functions import ackley, rastrigin, rosenbrock, sphere


@pytest.mark.parametrize("vector, dimension", [([0] * 10, 10), ([0] * 30, 30)])
def test_ackley_global_minimum(vector, dimension):
    assert math.isclose(ackley(vector), 0, abs_tol=1e-9)


@pytest.mark.parametrize("vector, dimension", [([0] * 10, 10), ([0] * 30, 30)])
def test_rastrigin_global_minimum(vector, dimension):
    assert math.isclose(rastrigin(vector), 0, abs_tol=1e-9)


@pytest.mark.parametrize("vector, dimension", [([1] * 10, 10), ([1] * 30, 30)])
def test_rosenbrock_global_minimum(vector, dimension):
    assert math.isclose(rosenbrock(vector), 0, abs_tol=1e-9)


@pytest.mark.parametrize("vector, dimension", [([0] * 10, 10), ([0] * 30, 30)])
def test_sphere_global_minimum(vector, dimension):
    assert math.isclose(sphere(vector), 0, abs_tol=1e-9)
