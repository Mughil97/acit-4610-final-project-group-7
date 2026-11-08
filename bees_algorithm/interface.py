from abc import ABC, abstractmethod


class OptimisationProblem(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def initialise_scout(self):
        pass

    @abstractmethod
    def evaluate(self):
        pass

    @abstractmethod
    def get_neighbour(self):
        pass
