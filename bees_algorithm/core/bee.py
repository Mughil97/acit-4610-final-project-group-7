class Bee:
    """Represent one candidate solution (e.g., a route in TSP or vector in continuous space).

    A site is a solution selected for local neighbourhood search; the best bees
    (lowest fitness) become elite sites.
    """

    def __init__(self, site, fitness, patch_size=0):
        self.stagnation_count = 0
        self.site = site
        self.fitness = fitness
        self.patch_size = patch_size

    def __str__(self):
        return f" Sol: {tuple(self.site)} | Fitness: {self.fitness} "
