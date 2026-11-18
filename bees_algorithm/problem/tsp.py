import random
import math

from bees_algorithm.interface import OptimisationProblem
from utils import load_data

#neighborus are created by swapping two cities (not first city) or reversing a segment

class SymmetricTSP(OptimisationProblem):

    def __init__(self, path_data, strategy):
        self.city_coordinates = load_data(path_data) #dictionary: key = ID, x and y corrdinates in a list
        self.strategy = strategy

        #distance matrix: one row and one column for every city
        self.distance_matrix = []


        #find the distances for every city by having one list (row) for every city, first row is for city 1

        for i in range(1, len(self.city_coordinates)+1): #so that we have last city as well
            liste = [] #distances from relevant city , index = 0 is distance to itself for first city
            city1_coordinates = self.city_coordinates[i]

            for j in range(1, len(self.city_coordinates)+1): # city 1 to itself is 0, so i include anyways 1 in the loop
                city2_coord = self.city_coordinates[j]
                distance = self.euclidean_dist(city1_coordinates, city2_coord)
                liste.append(distance)

            self.distance_matrix.append(liste) 


    def euclidean_dist(self,coordinates1,coordnates2):
        #coordinates are lists: [x1,y1]
        x1 = coordinates1[0]
        y1 = coordinates1[1]

        x2 = coordnates2[0]
        y2 = coordnates2[1]
 
        euclid = math.sqrt(((x1-x2)**2 + (y1-y2)**2 )) #always get a pos. number here 

        #add 0.5 then round down:
        distance = math.floor(euclid + 0.5)

        return distance
        

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

        for index in range(len(route)):
            city_ID = route[index] #from 1 to...

            #city_ID starts at 1, but it would be 0 in the matrix
        
            #first index = the distances from that city_ID
            #second index = the distance from the relevant city to the neighbour

            if index == len(route)-1: #last city
                total_dist += self.distance_matrix[city_ID-1][0] #back to city 1
                break

            city_ID_2 = route[index+1] #neighbour
            total_dist+= self.distance_matrix[city_ID-1][city_ID_2-1]

        return total_dist
        

    def get_neighbours(self, existing_route): #generate a neighbouring solution
        
        copy_route = list(existing_route) #w/o referencing

        i, j = 1, 0
        while i != j or i > j:
            #city 1 (index 0) cannot be incldued 
            i = random.randint(1,len(self.city_coordinates)-1) #both int included
            j = random.randint(1,len(self.city_coordinates)-1)

        if self.strategy == "swap":
            copy_route[i], copy_route[j] = copy_route[j], copy_route[i]

            
        else: #reverse btw two positions (inc endpoints in case we only choose i=2 and j=4 - no new neighbour if we didnt include endpoints)
            segment = copy_route[i:j+1] #start is incl, stop isnt: so +1 to exlude start
            segment.reverse()
            copy_route[i:j+1] = segment #replace with the reverse one

        return copy_route #new neighbour

    


        
