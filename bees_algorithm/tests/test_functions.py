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


@pytest.mark.parametrize(
    "vector, dimension, result",
    [
        (
            [
                1.178222,
                -14.983923,
                -17.931585,
                -14.234476,
                -9.156835,
                12.784657,
                2.757082,
                -12.296443,
                -18.874835,
                -13.255064,
            ],
            10,
            19.79201,
        ),
        (
            [
                -21.958462,
                17.177071,
                30.523729,
                -31.573072,
                20.130198,
                -28.731631,
                19.060645,
                18.075034,
                23.170631,
                22.288966,
                21.304656,
                16.198179,
                -15.077585,
                14.164669,
                31.119404,
                32.423098,
                -24.873207,
                3.291273,
                -2.312670,
                -2.564992,
                -15.551682,
                -6.612818,
                17.428149,
                14.654507,
                -15.706729,
                3.316818,
                -27.193334,
                -28.793050,
                2.240464,
                26.200188,
            ],
            30,
            21.40803,
        ),
    ],
)
def test_ackley_random_vector(vector, dimension, result):
    assert round(ackley(vector), 5) == result


@pytest.mark.parametrize(
    "vector, dimension, result",
    [
        (
            [
                4.01422206,
                -2.08052526,
                -0.04815559,
                -2.41901226,
                -3.59881665,
                1.11936221,
                -4.91995390,
                1.39603782,
                4.38334370,
                -3.96010308,
            ],
            10,
            179.7727,
        ),
        (
            [
                -2.0057250,
                0.9369819,
                2.1110108,
                2.6243512,
                1.6465621,
                2.6588855,
                -1.1989362,
                0.8466655,
                -4.4860313,
                -3.6447221,
                1.0723455,
                -1.6705083,
                3.4859851,
                4.2017025,
                3.4334149,
                -2.1583610,
                3.2522192,
                -5.0491543,
                1.6327437,
                0.2282077,
                1.3718480,
                -0.9751138,
                4.4940636,
                -4.9920919,
                -1.0605694,
                -1.0810406,
                -2.5634263,
                -1.4285713,
                0.4962433,
                -4.6826793,
            ],
            30,
            544.3341,
        ),
    ],
)
def test_rastrigin_random_vector(vector, dimension, result):
    assert round(rastrigin(vector), 5) == result


@pytest.mark.parametrize(
    "vector, dimension, result",
    [
        (
            [
                4.6384384,
                2.5873760,
                -2.4053787,
                -2.2181949,
                8.7916884,
                3.3223034,
                4.9135152,
                0.5722553,
                4.3002099,
                2.2369765,
            ],
            10,
            686627.1,
        ),
        (
            [
                1.4487633,
                -2.9103558,
                1.8319243,
                9.1732225,
                -0.2902818,
                -1.8336490,
                -1.9787986,
                7.7234249,
                -4.0915683,
                6.0335297,
                9.9436398,
                5.4096073,
                1.6100974,
                4.9824974,
                -1.1059083,
                5.9060004,
                5.1233724,
                2.3282243,
                -1.6932591,
                -2.9778815,
                7.8879931,
                4.8585386,
                -3.3251071,
                0.0303845,
                -3.9273664,
                1.6072278,
                3.8857788,
                7.4705295,
                -1.1772975,
                2.6828618,
            ],
            30,
            3155965.4,
        ),
    ],
)
def test_rosenbrock_random_vector(vector, dimension, result):
    assert round(rosenbrock(vector), 1) == result


@pytest.mark.parametrize(
    "vector, dimension, result",
    [
        (
            [
                -4.59777286,
                1.62872353,
                -4.25766494,
                1.55570513,
                1.59140997,
                1.22924029,
                -3.03319082,
                -0.01192787,
                -3.10718768,
                0.93681328,
            ],
            10,
            68.11643,
        ),
        (
            [
                -3.32373868,
                2.81361377,
                -2.27477008,
                -2.10870791,
                -3.07046169,
                4.28244740,
                -3.93884953,
                -1.45269024,
                3.96518131,
                3.32411562,
                0.09995212,
                -1.85244756,
                3.47329432,
                1.38656039,
                -3.81315012,
                -2.18022274,
                2.18719971,
                3.88604459,
                3.56081872,
                -2.34316041,
                1.24324613,
                -1.76014191,
                -0.09782635,
                2.76857050,
                2.07848446,
                -3.32481574,
                3.90484375,
                -0.51108045,
                -4.91979710,
                2.44100807,
            ],
            30,
            248.89035,
        ),
    ],
)
def test_sphere_random_vector(vector, dimension, result):
    assert round(sphere(vector), 5) == result
