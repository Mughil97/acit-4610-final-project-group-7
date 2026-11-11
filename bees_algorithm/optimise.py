import time

from logger import get_logger
from bees_algorithm.configs import (
    BENCHMARK_FUNCTIONS,
    DIMENSIONS,
    EXPERIMENT_RUNS,
    SEED,
)
from bees_algorithm.configs import FunctionOptimisationConfig as foc
from bees_algorithm.core.solver import BeesAlgorithmSolver
from bees_algorithm.problem.continuous import ContinuousFunctionOptimisation

logger = get_logger(__name__)


def optimise_functions():
    for func_config in BENCHMARK_FUNCTIONS:
        func = func_config.function
        for dim in DIMENSIONS:
            for run in range(EXPERIMENT_RUNS):
                seed = SEED + run

                cfo = ContinuousFunctionOptimisation(
                    seed, func_config.lower, func_config.upper, dim, func
                )

                solver = BeesAlgorithmSolver(problem=cfo, config=foc)
                start = time.perf_counter_ns()
                best_solution = solver.run()
                end = time.perf_counter_ns()

                logger.info(
                    f"Run: {run+1} | Dim: {dim} | Function: {func.__name__} | Best Fitness: {best_solution.fitness} | Execution time: {(end-start)/1e-9} | {best_solution.site}"
                )
