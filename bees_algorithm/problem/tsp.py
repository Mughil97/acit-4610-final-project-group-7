import random

from bees_algorithm.interface import OptimisationProblem
from utils import load_data

#neighborus are created by swapping two cities (not first city) or reversing a segment

class SymmetricTSP(OptimisationProblem):

    def __init__(self, path_data, strategy):
        self.city_coordinates = load_data(path_data)
        #dictionary: key = ID, x and y corrdinates in a list
        self.strategy = strategy

        #distance matrix: one row and one column for every city
        self.distance_matrix = []


        for i in self.city_coordinates.keys():
            liste = []
            liste.append[i]
            self.distance_matrix


        

    def initialise_scout(self): #generate random solution (a Bee)
        perm = [] #collection of all city IDs
        for k in self.city_coordinates.keys():
            perm.append(k)
        perm.remove(1) #remove city 1 because it needs to be first and Ill shuffle the list randomly

        #randomy shuffle the list to create a random solution
        random.shuffle(perm)
        perm.insert(0,1) #insert city 1 at index 0

        return perm

        

    def evaluate(self, route): #calcualte quality fo a solution
        #route is a permuation
        total_dist = 0
        for city_ID in route:
           
            #city_ID starts at 1, but it would be 0 in the matrix
            #city_ID+1 is hte neighbouring city in the route to city_ID
            #first index = the distances for that city
            #second index = the distance from the relevant city to the neighbour

            if city_ID == route[-1]: #last city
                total_dist += self.distance_matrix[city_ID-1][0] #back to city 1
            
            total_dist+= self.distance_matrix[city_ID-1][city_ID+1]

        return total_dist
        

    def get_neighbours(self): #generate a neighbouring solution
        # TODO: implement the initialisation
        pass
