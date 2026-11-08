from bees_algorithm.configs import (
    BENCHMARK_FUNCTIONS,
    DIMENSIONS,
    EXPERIMENT_RUNS,
    SEED,
)
from bees_algorithm.configs import FunctionOptimisationConfig as foc
from bees_algorithm.core.solver import BeesAlgorithmSolver
from bees_algorithm.problem.continuous import ContinuousFunctionOptimisation


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
                best_solution = solver.run()

                print(
                    f"Run: {run+1} | Dim: {dim} | Function: {func.__name__} | Best Fitness: {best_solution.fitness}"
                )
