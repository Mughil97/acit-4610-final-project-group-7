from collections.abc import Callable
from dataclasses import dataclass

from bees_algorithm.functions import ackley, rastrigin, rosenbrock, sphere


# ============================= Function Optimisation Config =============================
@dataclass(frozen=True)
class FunctionOptimisationConfig:
    max_evaluations: int = 30000
    ns: int = 30  # Scouts (total nr of bees)
    ne: int = 3  # Elites (elite sites)
    nb: int = 10  # Selected sites (Top selected sites includes elites)
    nre: int = 10  # Elite recruits (bees)
    nrb: int = 5  # Selected recruits (bees)
    stlim: int = 15  # Stagnation count
    ngh: float = 0.1  # Initial patch size; 10% of allowed range
    shrink_factor: float = 0.8  # 80% reduction in patch size


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


# ============================= TSP Config =============================
@dataclass(frozen=True)
class TSPConfig:
    max_evaluations: int = 30000
    ns: int = 30  # Scouts (total nr of bees)
    ne: int = 3  # Elites (elite sites)
    nb: int = 10  # Selected sites (Top selected sites includes elites)
    nre: int = 10  # Elite recruits (bees)
    nrb: int = 5  # Selected recruits (bees)
    stlim: int = 15  # Stagnation count
    ngh: float = 0.1  # Initial patch size; 10% of allowed range
    shrink_factor: float = 0.8  # 80% reduction in patch size


@dataclass(frozen=True)
class TSPInstanceConfig:
    name: str
    path: str
    cities: int
    optimum: int


EIL51_CONFIG = TSPInstanceConfig(
    name="eil51", path=r"bees_algorithm/data/eil51.tsp", cities=51, optimum=426
)
BERLIN52_CONFIG = TSPInstanceConfig(
    name="berlin52", path=r"bees_algorithm/data/berlin52.tsp", cities=52, optimum=7542
)
ST70_CONFIG = TSPInstanceConfig(
    name="st70", path=r"bees_algorithm/data/st70.tsp", cities=70, optimum=675
)
EIL76_CONFIG = TSPInstanceConfig(
    name="eil76", path=r"bees_algorithm/data/eil76.tsp", cities=76, optimum=538
)
KROA100_CONFIG = TSPInstanceConfig(
    name="kroA100", path=r"bees_algorithm/data/kroA100.tsp", cities=100, optimum=21282
)
CH150_CONFIG = TSPInstanceConfig(
    name="ch150", path=r"bees_algorithm/data/ch150.tsp", cities=150, optimum=6528
)

TSP_INSTANCES = [
    EIL51_CONFIG,
    BERLIN52_CONFIG,
    ST70_CONFIG,
    EIL76_CONFIG,
    KROA100_CONFIG,
    CH150_CONFIG,
]

TSPLIBS = {inst.name: inst.path for inst in TSP_INSTANCES}
TSP_OPTIMA = {inst.name: inst.optimum for inst in TSP_INSTANCES}

SWAP = "SWAP"
REVERSE = "REVERSE"
NEIGHBOURHOOD_VERSIONS = [SWAP, REVERSE]
