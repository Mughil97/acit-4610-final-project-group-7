import argparse
import time

from bees_algorithm.configs import (
    BENCHMARK_FUNCTIONS,
    DIMENSIONS,
    EXPERIMENT_RUNS,
    NEIGHBOURHOOD_VERSIONS,
    REVERSE,
    SEED,
    TSP_INSTANCES,
)
from bees_algorithm.configs import FunctionOptimisationConfig as foc
from bees_algorithm.configs import TSPConfig as tspc
from bees_algorithm.core.solver import BeesAlgorithmSolver
from bees_algorithm.problem.continuous import ContinuousFunctionOptimisation
from bees_algorithm.problem.tsp import SymmetricTSP
from bees_algorithm.utils.exceptions import BudgetExhausted
from bees_algorithm.utils.plotting import generate_all_plots_bees
from bees_algorithm.utils.summarizer import summarize_all_bees
from bees_algorithm.utils.tracked import TrackedProblem
from bees_algorithm.utils.validators import (
    validate_continuous_vector,
    validate_tsp_tour,
)
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
                tracked = TrackedProblem(tsp, tspc.ns, tspc.max_evaluations)

                solver = BeesAlgorithmSolver(problem=tracked, config=tspc)
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


def run_single_tsp(instance_name: str, neighbourhood: str = REVERSE, seed: int = SEED) -> None:
    """Execute one standalone TSP run without overwriting saved full-experiment files."""
    tsp_cfg = next(cfg for cfg in TSP_INSTANCES if cfg.name == instance_name)
    tsp = SymmetricTSP(seed, tsp_cfg.path, neighbourhood)
    tracked = TrackedProblem(tsp, tspc.ns, tspc.max_evaluations)
    solver = BeesAlgorithmSolver(problem=tracked, config=tspc)

    start = time.perf_counter_ns()
    try:
        solver.run()
    except BudgetExhausted:
        pass
    run_time = (time.perf_counter_ns() - start) / 1e9

    tracker = tracked.tracker
    route = list(tracker.best_solution.site)
    final_best = float(tracker.best_solution.fitness)
    initial_best = float(tracker.initial_best.fitness)
    gap_pct = 100.0 * (final_best - tsp_cfg.optimum) / tsp_cfg.optimum
    is_valid, errors = validate_tsp_tour(
        route=route,
        city_coordinates=tsp.city_coordinates,
        distance_matrix=tsp.distance_matrix,
        reported_length=final_best,
    )
    logger.info(
        f"TSP Single Run | instance={tsp_cfg.name} | neighbourhood={neighbourhood} | "
        f"seed={seed} | initial_best={initial_best:.0f} | final_best={final_best:.0f} | "
        f"optimum={tsp_cfg.optimum} | gap={gap_pct:.2f}% | valid={is_valid} | "
        f"evaluations={tracker.evaluations} | runtime={run_time:.3f}s"
    )
    if errors:
        logger.warning(f"Validation errors: {errors}")


def run_single_function(function_name: str, dimension: int = 10, seed: int = SEED) -> None:
    """Execute one standalone continuous run without overwriting saved full-experiment files."""
    func_config = next(
        cfg for cfg in BENCHMARK_FUNCTIONS if cfg.function.__name__ == function_name
    )
    cfo = ContinuousFunctionOptimisation(
        seed, func_config.lower, func_config.upper, dimension, func_config.function
    )
    tracked = TrackedProblem(cfo, foc.ns, foc.max_evaluations)
    solver = BeesAlgorithmSolver(problem=tracked, config=foc)

    start = time.perf_counter_ns()
    try:
        solver.run()
    except BudgetExhausted:
        pass
    run_time = (time.perf_counter_ns() - start) / 1e9

    tracker = tracked.tracker
    vector = [float(x) for x in tracker.best_solution.site]
    final_best = float(tracker.best_solution.fitness)
    initial_best = float(tracker.initial_best.fitness)
    is_valid, errors = validate_continuous_vector(
        vector=vector,
        dimension=dimension,
        lower=func_config.lower,
        upper=func_config.upper,
        func=func_config.function,
        reported_value=final_best,
    )
    logger.info(
        f"Continuous Single Run | function={function_name} | D={dimension} | "
        f"seed={seed} | initial_best={initial_best:.6g} | final_best={final_best:.6g} | "
        f"valid={is_valid} | evaluations={tracker.evaluations} | runtime={run_time:.3f}s"
    )
    if errors:
        logger.warning(f"Validation errors: {errors}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Problem 1 (Bees Algorithm): full experiment set or a single run."
    )
    parser.add_argument(
        "--part",
        choices=("all", "tsp", "continuous"),
        default="all",
        help="Experiment part to run when executing the full set (default: all).",
    )
    parser.add_argument(
        "--instance",
        choices=[cfg.name for cfg in TSP_INSTANCES],
        default=None,
        help="Run a single TSP instance (Part A).",
    )
    parser.add_argument(
        "--neighbourhood",
        choices=NEIGHBOURHOOD_VERSIONS,
        default=REVERSE,
        help="Neighbourhood version for a single TSP run (default: REVERSE).",
    )
    parser.add_argument(
        "--function",
        choices=[cfg.function.__name__ for cfg in BENCHMARK_FUNCTIONS],
        default=None,
        help="Run a single continuous benchmark function (Part B).",
    )
    parser.add_argument(
        "--dimension",
        type=int,
        choices=DIMENSIONS,
        default=10,
        help="Dimension for a single continuous run (default: 10).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=SEED,
        help=f"Random seed for a single run (default: {SEED}).",
    )
    args = parser.parse_args()

    if args.instance and args.function:
        parser.error("Specify either --instance (Part A) or --function (Part B), not both.")

    if args.instance is not None:
        run_single_tsp(args.instance, args.neighbourhood, args.seed)
        return

    if args.function is not None:
        run_single_function(args.function, args.dimension, args.seed)
        return

    writer = ExperimentWriter()
    if args.part in ("all", "tsp"):
        optimise_tsp(writer=writer)
    if args.part in ("all", "continuous"):
        optimise_functions(writer=writer)
    summarize_all_bees()
    generate_all_plots_bees()


if __name__ == "__main__":
    main()
