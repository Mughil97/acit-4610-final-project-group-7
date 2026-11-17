from bees_algorithm.optimise import optimise_functions, optimise_tsp
from logger import get_logger

if __name__ == "__main__":
    logger = get_logger("main")
    optimise_tsp()
    optimise_functions()
