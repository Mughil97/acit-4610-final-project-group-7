from bees_algorithm.core.bee import Bee


class BeesAlgorithmSolver:

    def __init__(self, problem, config):
        self.problem = problem
        self.config = config
        self.evaluations = 0
        self.scouts = []
        self.global_best = None

    def initialise(self):
        for _ in range(self.config.ns):
            vector = self.problem.initialise_scout()
            fitness = self.problem.evaluate(vector)
            self.scouts.append(Bee(vector, fitness))
            self.evaluations += 1

    def rank_and_split_sites(self):
        scouts = sorted(self.scouts, key=lambda bee: bee.fitness)
        self.global_best = scouts[0]
        elites = scouts[: self.config.ne]
        best = scouts[self.config.ne : self.config.nb]

        return elites, best

    def exploit_site(self, sites, recruit_count):

        for site in sites:
            for _ in range(recruit_count):

                if self.evaluations >= self.config.max_evaluations:
                    break

                neighbour_vector = self.problem.get_neighbour(site.site)
                fitness = self.problem.evaluate(neighbour_vector)
                self.evaluations += 1

                if fitness < site.fitness:
                    site.site = neighbour_vector
                    site.fitness = fitness
                    site.stagnation_count = 0
                else:
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
        for _ in range(count):
            vector = self.problem.initialise_scout()
            fitness = self.problem.evaluate(vector)
            self.scouts.append(Bee(vector, fitness))
            self.evaluations += 1

    def run(self):
        self.initialise()

        while self.evaluations < self.config.max_evaluations:

            elites, best = self.rank_and_split_sites()

            self.exploit_site(elites, self.config.nre)
            self.exploit_site(best, self.config.nrb)

            # abandon_count = self.abandon_stagnated_sites()
            self.replenish_scouts((self.config.ns - self.config.nb))

        return self.global_best
