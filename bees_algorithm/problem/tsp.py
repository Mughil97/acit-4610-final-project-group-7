import math
import random
from copy import deepcopy

from bees_algorithm.configs import SWAP, NEIGHBOURHOOD_VERSIONS, REVERSE
from bees_algorithm.interface import OptimisationProblem
from bees_algorithm.utils.load_data import load_data

# Neighbours are created by swapping two cities (not first city) or reversing a segment


class SymmetricTSP(OptimisationProblem):

    def __init__(self, seed, path_data, strategy):
        self.rand = random.Random(seed)
        self.city_coordinates = load_data(
            path_data
        )  # dictionary: key = city id, x and y coordinates in a list
        self.strategy = strategy

        # distance matrix: one row and one column for every city
        # The distance to the self city will be 0 i.e city 1 to city 1 will be 0
        #      1  2  3  4
        # 1 | 00 10 20 30 |
        # 2 | 10 00 15 25 |
        # 3 | 20 15 00 35 |
        # 4 | 30 25 35 00 |
        self.distance_matrix = []

        # find the distances for every city by having one list (row) for every city, first row is for city 1
        for i, city1 in self.city_coordinates.items():  # Row
            row = []
            for j, city2 in self.city_coordinates.items():  # Column
                row.append(self.euclidean_dist(city1, city2))
            self.distance_matrix.append(row)

    @property
    def problem_type(self):
        return "TSP"

    def euclidean_dist(self, coordinates1, coordinates2):
        # coordinates are lists: [x1,y1]
        x1 = coordinates1[0]
        y1 = coordinates1[1]

        x2 = coordinates2[0]
        y2 = coordinates2[1]

        euclid = math.sqrt(
            ((x1 - x2) ** 2 + (y1 - y2) ** 2)
        )  # always get a positive number here

        # add 0.5 then round down:
        distance = math.floor(euclid + 0.5)

        return distance

    def initialise_scout(self):  # generate random solution (a Bee)
        # City 1 will always be the first city; so it will be added after the shuffle
        city_permutation = list(range(2, len(self.city_coordinates) + 1))

        # randomly shuffle the list to create a random solution
        self.rand.shuffle(city_permutation)

        # The city 1 is alway
        city_permutation.insert(0, 1)

        return city_permutation

    def evaluate(self, route):  # calculate quality fo a solution
        # route is a permutation
        total_dist = 0

        for index in range(len(route)):
            city1_id = route[index]  # from 1 to...

            # city_ID starts at 1, but it would be 0 in the matrix

            # first index = the distances from that city_ID
            # second index = the distance from the relevant city to the neighbour

            if index == len(route) - 1:  # last city
                total_dist += self.distance_matrix[city1_id - 1][0]  # back to city 1
                break

            city2_id = route[index + 1]  # neighbour
            total_dist += self.distance_matrix[city1_id - 1][city2_id - 1]

        return total_dist

    def get_neighbour(self, bee):  # generate a neighbouring solution

        if self.strategy not in NEIGHBOURHOOD_VERSIONS:
            raise ValueError("Invalid strategy.")

        bee = deepcopy(bee)  # w/o referencing
        route = bee.site

        # Pick two distinct indices with 1 <= i < j <= n - 1 (city 1 at index 0 stays fixed)

        # The list index starts from 0 to n-1. Since city 1 is always at 0'th position
        # we need to do n-2 so we can perform operations from 1 to n-1
        max_possible_span = len(route) - 2

        patch_ratio = (
            bee.patch_size if bee.patch_size > 0 else 1.0
        )  # Safety check to make sure patch_size is not None

        # Restrict the maximum index distance |j - i| using the bee's current patch_size
        max_span = max(
            1, min(max_possible_span, math.ceil(max_possible_span * patch_ratio))
        )

        span = self.rand.randint(1, max_span)  # From 1 to max span

        i = self.rand.randint(1, len(route) - 1 - span)
        j = i + span

        if self.strategy == SWAP:
            route[i], route[j] = route[j], route[i]

        elif (
            self.strategy == REVERSE
        ):  # reverse segment between i and j (inclusive of both endpoints)
            segment = route[i : j + 1]
            segment.reverse()
            route[i : j + 1] = segment  # replace with the reversed segment

        return route  # new neighbour
