from bees_algorithm.core.bee import Bee
from logger import get_logger

logger = get_logger(__name__)


class BeesAlgorithmSolver:

    def __init__(self, problem, config):
        self.problem = problem
        self.config = config
        self.evaluations = 0
        self.scouts = [] #list of bees
        self.global_best = None

    def initialise(self):  #initialise the population
        for _ in range(self.config.ns):
            vector = self.problem.initialise_scout()
            fitness = self.problem.evaluate(vector)
            self.scouts.append(Bee(vector, fitness))
            self.evaluations += 1

    def rank_and_split_sites(self):
        scouts = sorted(self.scouts, key=lambda bee: bee.fitness)
        #for each bee, compare and sort using its fitness: lower first

       # if self.global_best is None or scouts[0].


        self.global_best = scouts[0] 
        elites = scouts[: self.config.ne] #3 first
        selected_sites = scouts[self.config.ne : self.config.nb] #7, but the elties are in so 10 total

        return elites, selected_sites

    def exploit_site(self, sites, recruit_count):

        for site in sites: #site = bee, solution
            for _ in range(recruit_count):

                if self.evaluations >= self.config.max_evaluations:
                    break

                neighbour_vector = self.problem.get_neighbour(site.site)
                fitness = self.problem.evaluate(neighbour_vector)
                self.evaluations += 1

                #greedy selection:
                if fitness < site.fitness: #if the neighbour is better, replace
                    site.site = neighbour_vector
                    site.fitness = fitness
                #     site.stagnation_count = 0
                # else:
                #     site.stagnation_count += 1

    # def abandon_stagnated_sites(self):
    #     active_scouts = []
    #     abandon_count = 0

    #     for site in self.scouts:
    #         if site.stagnation_count >= self.config.stlim:
    #             abandon_count += 1
    #         else:
    #             active_scouts.append(site)

    #     self.scouts = active_scouts

    #     return abandon_count


#Generates new random scout bees, as the remaining pop (not selected + elites) are discared
#We generate new scouts to mainint pop diversity and exlore new areas

    def replenish_scouts(self, count):
        for _ in range(count):
            vector = self.problem.initialise_scout()
            fitness = self.problem.evaluate(vector)
            self.scouts.append(Bee(vector, fitness))
            self.evaluations += 1

    def run(self):
        self.initialise()

        while self.evaluations < self.config.max_evaluations:

            elites, selected_sites = self.rank_and_split_sites()

            self.exploit_site(elites, self.config.nre)
            self.exploit_site(selected_sites, self.config.nrb)

            self.scouts = elites + selected_sites

            self.replenish_scouts((self.config.ns - self.config.nb))

        return self.global_best
