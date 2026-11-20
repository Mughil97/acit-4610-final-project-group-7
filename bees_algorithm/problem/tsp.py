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
        )  # dictionary: key = ID, x and y coordinates in a list
        self.strategy = strategy

        # distance matrix: one row and one column for every city
        self.distance_matrix = []

        # find the distances for every city by having one list (row) for every city, first row is for city 1

        for i in range(
            1, len(self.city_coordinates) + 1
        ):  # so that we have last city as well
            liste = (
                []
            )  # distances from relevant city , index = 0 is distance to itself for first city
            city1_coordinates = self.city_coordinates[i]

            for j in range(
                1, len(self.city_coordinates) + 1
            ):  # city 1 to itself is 0, so i include anyways 1 in the loop
                city2_coord = self.city_coordinates[j]
                distance = self.euclidean_dist(city1_coordinates, city2_coord)
                liste.append(distance)

            self.distance_matrix.append(liste)

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
        )  # always get a pos. number here

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
            city_ID = route[index]  # from 1 to...

            # city_ID starts at 1, but it would be 0 in the matrix

            # first index = the distances from that city_ID
            # second index = the distance from the relevant city to the neighbour

            if index == len(route) - 1:  # last city
                total_dist += self.distance_matrix[city_ID - 1][0]  # back to city 1
                break

            city_ID_2 = route[index + 1]  # neighbour
            total_dist += self.distance_matrix[city_ID - 1][city_ID_2 - 1]

        return total_dist

    def get_neighbour(self, bee):  # generate a neighbouring solution

        if self.strategy not in NEIGHBOURHOOD_VERSIONS:
            raise ValueError("Invalid strategy.")

        bee = deepcopy(bee)  # w/o referencing
        route = bee.site

        # Pick two distinct indices with 1 <= i < j <= n - 1 (city 1 at index 0 stays fixed)
        i, j = sorted(self.rand.sample(range(1, len(route)), 2))

        if self.strategy == SWAP:
            route[i], route[j] = route[j], route[i]

        elif (
            self.strategy == REVERSE
        ):  # reverse segment between i and j (inclusive of both endpoints)
            segment = route[i : j + 1]
            segment.reverse()
            route[i : j + 1] = segment  # replace with the reversed segment

        return route  # new neighbour
