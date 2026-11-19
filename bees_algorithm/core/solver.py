from bees_algorithm.core.bee import Bee
from logger import get_logger

logger = get_logger(__name__)


class BeesAlgorithmSolver:

    def __init__(self, problem, config):
        self.problem = problem
        self.config = config
        self.scouts = []

    def initialise(self):
        """
        Initialises the population/solutions
        """
        for _ in range(self.config.ns):
            vector = self.problem.initialise_scout()
            fitness = self.problem.evaluate(vector)
            self.scouts.append(Bee(vector, fitness, self.config.shrink_factor))

    def rank_and_split_sites(self):
        scouts = sorted(
            self.scouts, key=lambda bee: bee.fitness
        )  # Sort the bee/solution using fitness, lower is better

        elites = scouts[: self.config.ne]
        selected_sites = scouts[self.config.ne : self.config.nb]

        return elites, selected_sites

    def exploit_site(self, sites, recruit_count):

        for site in sites:  # Site is a bee/solution
            site_stagnated = True
            for _ in range(recruit_count):

                neighbour_vector = self.problem.get_neighbour(site)
                fitness = self.problem.evaluate(neighbour_vector)

                # Greedy selection
                if fitness < site.fitness:  # If the neighbour is bette,replace
                    site.site = neighbour_vector
                    site.fitness = fitness
                    site.stagnation_count = 0
                    site_stagnated = False

            if site_stagnated:
                site.stagnation_count += 1

    def abandon_stagnated_sites(self):
        active_scouts = []
        abandon_count = 0

        for site in self.scouts:
            if site.stagnation_count >= self.config.stlim:
                abandon_count += 1
            else:
                active_scouts.append(site)

        self.scouts = active_scouts

        return abandon_count

    def replenish_scouts(self, count):
        """
        Generates new random scout bees for the remaining population i.e. (ns - (nb + abandoned sites))
        This new scouts search the global space randomly so its exploration.
        """

        for _ in range(count):
            vector = self.problem.initialise_scout()
            fitness = self.problem.evaluate(vector)
            self.scouts.append(Bee(vector, fitness, self.config.shrink_factor))

    def run(self):
        self.initialise()

        while True:  # The evaluations are tracked in a different helper class

            elites, selected_sites = self.rank_and_split_sites()

            self.exploit_site(elites, self.config.nre)
            self.exploit_site(selected_sites, self.config.nrb)

            self.scouts = elites + selected_sites

            abandoned = self.abandon_stagnated_sites()

            self.replenish_scouts((self.config.ns - (self.config.nb + abandoned)))

    def save_experiment(self, run_time):
        self.problem.save_experiment(run_time)
