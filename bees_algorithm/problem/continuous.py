"""Continuous optimisation problem wrapper.

In continuous optimisation, a solution is a vector of real numbers
where each number represents one decision variable.
"""

import random

from bees_algorithm.interface import OptimisationProblem

# benchmark function: standardized test function to evaluate and compare the performance of optimization algo
# seed determines the random nr generator's initial state


class ContinuousFunctionOptimisation(OptimisationProblem):

    def __init__(self, seed, lower, upper, dimension, function):
        self.rand = random.Random(seed)
        self.lower = lower
        self.upper = upper
        self.dimension = dimension
        self.function = function
        self.allowed_range = upper - lower

    @property
    def problem_type(self):
        return "CONTINUOUS"

    def initialise_scout(self):
        # generate a new random solution for every coordinate
        return [
            self.rand.uniform(self.lower, self.upper) for _ in range(self.dimension)
        ]

    def evaluate(self, vector):
        # the function calculates how good it is (lower is better)
        return self.function(vector)

    # generate new solution and returns the complete neighbouring solution
    # in min: make sure that the new coordinate is not above the upperbound
    # in max: make sure it is not below the lower bound
    def get_neighbour(self, bee):
        # New solution/bee has 10% of allowed range and if they dont improve the range reduces by a factor of shrink_factor
        allowed_range = self.allowed_range * bee.patch_size

        return [
            max(
                self.lower,
                min(
                    self.upper,
                    i + self.rand.uniform(-allowed_range, allowed_range),
                ),
            )
            for i in bee.site
        ]
