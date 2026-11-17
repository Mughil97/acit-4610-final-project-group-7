import time

from bees_algorithm.configs import (
    BENCHMARK_FUNCTIONS,
    DIMENSIONS,
    EXPERIMENT_RUNS,
    NEIGHBOURHOOD_VERSIONS,
    SEED,
    TSPLIBS,
)
from bees_algorithm.configs import FunctionOptimisationConfig as foc
from bees_algorithm.configs import TSPConfig as tspc
from bees_algorithm.core.solver import BeesAlgorithmSolver
from bees_algorithm.problem.continuous import ContinuousFunctionOptimisation
from bees_algorithm.problem.tsp import SymmetricTSP
from bees_algorithm.utils.exceptions import BudgetExhausted
from bees_algorithm.utils.tracked import TrackedProblem
from logger import get_logger

logger = get_logger(__name__)


def optimise_functions():
    logger.info(
        "==========  Continuous Function Optimisation (Problem 1 Part B) =========="
    )
    for func_config in BENCHMARK_FUNCTIONS:
        func = func_config.function
        logger.info(f"Function: {func.__name__}")

        for dim in DIMENSIONS:
            logger.info(f"Dimension: {dim}")

            for run in range(EXPERIMENT_RUNS):
                seed = SEED + run
                logger.info(f"Run: {run+1} | Seed: {seed}")

                cfo = ContinuousFunctionOptimisation(
                    seed, func_config.lower, func_config.upper, dim, func
                )
                tracked = TrackedProblem(cfo, foc.ns, foc.max_evaluations)

                solver = BeesAlgorithmSolver(problem=tracked, config=foc)
                start = time.perf_counter_ns()
                try:
                    solver.run()
                except BudgetExhausted:
                    pass
                end = time.perf_counter_ns()

                run_time = (end - start) / 1e9

                solver.save_experiment(run_time)

            logger.info("\n")

        logger.info(
            "------------------------------------------------------------------------------------\n"
        )


def optimise_tsp():
    logger.info("==========  TSP (Problem 1 Part A) ==========")
    for lib, path in TSPLIBS.items():
        logger.info(f"Library: {lib}")

        for version in NEIGHBOURHOOD_VERSIONS:
            logger.info(f"Version: {version}")

            for run in range(EXPERIMENT_RUNS):
                seed = SEED + run
                logger.info(f"Run: {run+1} | Seed: {seed}")

                tsp = SymmetricTSP(seed, path, version)
                tracked = TrackedProblem(tsp, foc.ns, foc.max_evaluations)

                solver = BeesAlgorithmSolver(problem=tracked, config=foc)
                start = time.perf_counter_ns()
                try:
                    solver.run()
                except BudgetExhausted:
                    pass
                end = time.perf_counter_ns()

                run_time = (end - start) / 1e9

                solver.save_experiment(run_time)

            logger.info("\n")

        logger.info(
            "------------------------------------------------------------------------------------\n"
        )
