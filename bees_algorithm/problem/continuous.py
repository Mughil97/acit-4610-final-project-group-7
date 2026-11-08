import random

from bees_algorithm.interface import OptimisationProblem


class ContinuousFunctionOptimisation(OptimisationProblem):

    def __init__(self, seed, lower, upper, dimension, function):
        self.rand = random.Random(seed)
        self.lower = lower
        self.upper = upper
        self.dimension = dimension
        self.function = function
        self.coordinate_offset = 0.1  # 10% as mentioned on the requirement

    def initialise_scout(self):
        return [
            self.rand.uniform(self.lower, self.upper) for _ in range(self.dimension)
        ]

    def evaluate(self, vector):
        return self.function(vector)

    def get_neighbour(self, vector):
        return [
            max(
                self.lower,
                min(
                    self.upper,
                    i
                    + self.rand.uniform(
                        -i * self.coordinate_offset, i * self.coordinate_offset
                    ),
                ),
            )
            for i in vector
        ]
