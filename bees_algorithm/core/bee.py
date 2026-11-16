class Bee:

    def __init__(self, site, fitness):
        # self.stagnation_count = 0
        self.site = site
        self.fitness = fitness

"""
A bee = one possible solution (route in TSP)
A site = a solution to explore further
The best bee (lowest fitness) becomes an elite site. 
We want to try to find better routes around this site.  
"""