from bees_algorithm.optimise import optimise_functions
from logger import get_logger

if __name__ == "__main__":
    logger = get_logger("main")
    optimise_functions()
    logger.info("Hello World!")
