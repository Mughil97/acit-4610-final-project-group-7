import random

from bees_algorithm.interface import OptimisationProblem


class ContinuousFunctionOptimisation(OptimisationProblem):

    def __init__(self, seed, lower, upper, dimension, function):
        self.rand = random.Random(seed)
        self.lower = lower
        self.upper = upper
        self.dimension = dimension
        self.function = function
        self.allowed_range = (
            upper - lower
        ) * 0.1  # 10% of the allowed range (upper - lower)

    @property
    def problem_type(self):
        return "CONTINUOUS"

    def initialise_scout(self):
        return [
            self.rand.uniform(self.lower, self.upper) for _ in range(self.dimension)
        ]

    def evaluate(self, vector):
        return self.function(vector)

    def get_neighbour(self, bee):
        scale = max(1e-6, (1 - bee.shrink_factor) ** bee.stagnation_count)
        allowed_range = self.allowed_range * scale

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
