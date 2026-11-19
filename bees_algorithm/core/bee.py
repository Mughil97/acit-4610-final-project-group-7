class Bee:

    def __init__(self, site, fitness, patch_size=0):
        self.stagnation_count = 0
        self.site = site
        self.fitness = fitness
        self.patch_size = patch_size

    def __str__(self):
        return f" Sol: {tuple(self.site)} | Fitness: {self.fitness} "


"""
A bee = one possible solution (route in TSP)
A site = a solution to explore further
The best bee (lowest fitness) becomes an elite site. 
We want to try to find better routes around this site.  
"""
