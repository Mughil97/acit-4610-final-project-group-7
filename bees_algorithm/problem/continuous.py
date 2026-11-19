import random

from bees_algorithm.interface import OptimisationProblem
"In continuous optimisation, a solution is a vector of real nrs. "
"Each nr: one decision variable"
#benchmark function: standardized test function to evaluate and compare the performance of optimization algo
#seed determines the random nr generator's initial state

class ContinuousFunctionOptimisation(OptimisationProblem):

    def __init__(self, seed, lower, upper, dimension, function):
        self.rand = random.Random(seed)
        self.lower = lower #min value allowed for each coordinate
        self.upper = upper #max value allowed for each coordinate
        self.dimension = dimension #nr of variables
        self.function = function #benchmark func being optimized

        #calculate the neighbourhood size
        self.allowed_range = (
            upper - lower
        ) * 0.1  # 10% of the allowed range (upper - lower)
        #each coordinate can change by a random amount between this range (inc hte endpoints)
        #teh range is the [-self.allowed_range, self.allowed_range]

    def initialise_scout(self):
        return [
            self.rand.uniform(self.lower, self.upper) for _ in range(self.dimension)
        ]
    #generate a new random solution for every coordinate

    def evaluate(self, vector):
        return self.function(vector) #the function calcuated how good it is
    #lower is better 


#generate new solution and returns the complete neighbouring solution
#in min: make sure that the new coordinate is not above the upperbound
#in max: make sure it is not below the lower band
    def get_neighbour(self, vector):
        return [
            max(
                self.lower,
                min(
                    self.upper,
                    i + self.rand.uniform(-self.allowed_range, self.allowed_range),
                ),
            )
            for i in vector #for every coordinate 
        ]
