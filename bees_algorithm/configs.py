from collections.abc import Callable
from dataclasses import dataclass

from bees_algorithm.functions import ackley, rastrigin, rosenbrock, sphere


@dataclass(frozen=True)
class FunctionOptimisationConfig:
    max_evaluations: int = 30000
    ns: int = 30  # Scouts
    ne: int = 3  # Elites
    nb: int = 10  # Best
    nre: int = 15  # Elite recruits
    nrb: int = 5  # Best recruits
    # stlim: int = 10  # Stagnation


@dataclass(frozen=True)
class FunctionConfig:
    function: Callable
    lower: float
    upper: float
    global_minimum: float


SPHERE_CONFIG = FunctionConfig(
    function=sphere, lower=-5.12, upper=5.12, global_minimum=0.0
)
ROSENBROCK_CONFIG = FunctionConfig(
    function=rosenbrock, lower=-5.0, upper=10.0, global_minimum=0.0
)
RASTRIGIN_CONFIG = FunctionConfig(
    function=rastrigin, lower=-5.12, upper=5.12, global_minimum=0.0
)
ACKLEY_CONFIG = FunctionConfig(
    function=ackley, lower=-32.768, upper=32.768, global_minimum=0.0
)

BENCHMARK_FUNCTIONS = [
    SPHERE_CONFIG,
    ROSENBROCK_CONFIG,
    RASTRIGIN_CONFIG,
    ACKLEY_CONFIG,
]

DIMENSIONS = [10, 30]
EXPERIMENT_RUNS = 10
SEED = 45
