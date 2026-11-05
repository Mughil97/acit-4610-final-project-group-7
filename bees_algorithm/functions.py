import math


def sphere(vector):
    return sum(x**2 for x in vector)


def rosenbrock(vector):
    return sum(
        (100 * (vector[i + 1] - vector[i] ** 2) ** 2) + (1 - vector[i]) ** 2
        for i in range(len(vector) - 1)
    )


def rastrigin(vector):
    return 10 * len(vector) + sum(x**2 - 10 * math.cos(2 * math.pi * x) for x in vector)


def ackley(vector):
    """
    The R implementation(https://www.sfu.ca/~ssurjano/Code/ackleyr.html) was adapted to python
    """
    dimension = len(vector)
    squared_sum = sum(x**2 for x in vector)
    cos_sum = sum(math.cos(2 * math.pi * x) for x in vector)

    first_term = -20 * math.exp(-0.2 * math.sqrt(squared_sum / dimension))
    second_term = -math.exp(cos_sum / dimension)

    return first_term + second_term + 20 + math.exp(1)
