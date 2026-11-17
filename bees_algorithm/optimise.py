import time

from bees_algorithm.configs import (
    BENCHMARK_FUNCTIONS,
    DIMENSIONS,
    EXPERIMENT_RUNS,
    NEIGHBOURHOOD_VERSIONS,
    SEED,
    TSP_INSTANCES,
)
from bees_algorithm.configs import FunctionOptimisationConfig as foc
from bees_algorithm.configs import TSPConfig as tspc
from bees_algorithm.core.solver import BeesAlgorithmSolver
from bees_algorithm.problem.continuous import ContinuousFunctionOptimisation
from bees_algorithm.problem.tsp import SymmetricTSP
from bees_algorithm.utils.exceptions import BudgetExhausted
from bees_algorithm.utils.tracked import TrackedProblem
from bees_algorithm.utils.writer import ExperimentWriter
from logger import get_logger

logger = get_logger(__name__)


def optimise_functions(writer: ExperimentWriter | None = None):
    if writer is None:
        writer = ExperimentWriter()
    seeds = [SEED + run for run in range(EXPERIMENT_RUNS)]
    writer.write_metadata(tsp_config=tspc, function_config=foc, seeds=seeds)
    writer.reset_part_b()

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
                writer.record_continuous_run(
                    function_name=func.__name__,
                    dimension=dim,
                    lower=func_config.lower,
                    upper=func_config.upper,
                    global_minimum=func_config.global_minimum,
                    run_idx=run + 1,
                    seed=seed,
                    tracker=tracked.tracker,
                    runtime_sec=run_time,
                    problem=cfo,
                )

            writer.flush_continuous_history(func.__name__, dim)
            logger.info("\n")

        logger.info(
            "------------------------------------------------------------------------------------\n"
        )


def optimise_tsp(writer: ExperimentWriter | None = None):
    if writer is None:
        writer = ExperimentWriter()
    seeds = [SEED + run for run in range(EXPERIMENT_RUNS)]
    writer.write_metadata(tsp_config=tspc, function_config=foc, seeds=seeds)
    writer.reset_part_a()

    logger.info("==========  TSP (Problem 1 Part A) ==========")
    for tsp_cfg in TSP_INSTANCES:
        logger.info(f"Library: {tsp_cfg.name}")

        for version in NEIGHBOURHOOD_VERSIONS:
            logger.info(f"Version: {version}")

            for run in range(EXPERIMENT_RUNS):
                seed = SEED + run
                logger.info(f"Run: {run+1} | Seed: {seed}")

                tsp = SymmetricTSP(seed, tsp_cfg.path, version)
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
                writer.record_tsp_run(
                    instance=tsp_cfg.name,
                    cities=tsp_cfg.cities,
                    optimum=tsp_cfg.optimum,
                    neighbourhood=version,
                    run_idx=run + 1,
                    seed=seed,
                    tracker=tracked.tracker,
                    runtime_sec=run_time,
                    problem=tsp,
                )

            writer.flush_tsp_history(tsp_cfg.name, version)
            logger.info("\n")

        logger.info(
            "------------------------------------------------------------------------------------\n"
        )
