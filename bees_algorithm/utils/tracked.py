import math
from copy import deepcopy

from bees_algorithm.core.bee import Bee
from bees_algorithm.interface import OptimisationProblem
from bees_algorithm.utils.exceptions import BudgetExhausted
from logger import get_logger

logger = get_logger(__name__)


class TrackedProblem(OptimisationProblem):
    """
    A wrapper to track the evaluations, log the metics and stop the experiment cleanly on max evaluations

    Args:
        problem (OptimisationProblem): The problem to be solved TSP or continuous
    """

    def __init__(self, problem, initial_population_size, max_evaluations):
        self.problem = problem
        self.tracker = ProblemTracker(initial_population_size, max_evaluations)

    @property
    def problem_type(self):
        return self.problem.problem_type

    def initialise_scout(self):
        return self.problem.initialise_scout()

    def evaluate(self, solution):
        if self.tracker.evaluations >= self.tracker.max_evaluations:
            raise BudgetExhausted("The budget exhausted. Stopping the experiment ..")

        fitness = self.problem.evaluate(solution)
        self.tracker.record(Bee(solution, fitness))  # To log the metrics
        return fitness

    def get_neighbour(self, solution):
        return self.problem.get_neighbour(solution)

    def save_experiment(self, run_time):
        logger.info(
            f"Initial Best: {self.tracker.initial_best.fitness} | Final Best: {self.tracker.best_solution.fitness} | Evaluations: {self.tracker.evaluations} | Runtime: {run_time}"
        )


class ProblemTracker:
    """
    A helper to track the evaluations and log the metrics.
    """

    def __init__(self, initial_population_size, max_evaluations):
        self.evaluations = 0
        self.max_evaluations = max_evaluations
        self.initial_population_size = initial_population_size

        self.best_solution = Bee(
            None, math.inf
        )  # The TSP and Continuous Function Optimisation are minimisation problem hence hardcoding infinity

        self.initial_best = None

        self.history = []

    def record(self, bee):
        """
        Records the no of evaluation, best-so-far
        """

        self.evaluations += 1

        if bee.fitness < self.best_solution.fitness:
            self.best_solution = deepcopy(
                bee
            )  # Create a copy so reference does not update the best

        if self.evaluations == self.initial_population_size:
            self.initial_best = deepcopy(self.best_solution)

        self.history.append(self.best_solution.fitness)
