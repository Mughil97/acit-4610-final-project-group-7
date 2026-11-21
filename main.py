from bees_algorithm.optimise import optimise_functions, optimise_tsp
from bees_algorithm.utils.plotting import generate_all_plots_bees
from bees_algorithm.utils.summarizer import summarize_all_bees
from bees_algorithm.utils.writer import ExperimentWriter
from evolution_strategy.build_summary import summarize_all_es
from evolution_strategy.export_experiments import optimise_es
from evolution_strategy.plot_results import generate_all_plots_es
from logger import get_logger

if __name__ == "__main__":
    logger = get_logger("main")
    writer = ExperimentWriter()
    optimise_tsp(writer=writer)
    optimise_functions(writer=writer)
    summarize_all_bees()
    generate_all_plots_bees()

    optimise_es()
    summarize_all_es()
    generate_all_plots_es()
