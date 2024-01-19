# Students:
# Bárbara Nóbrega Galiza - 105937
# Pedro Daniel Fidalgo de Pinho - 109986

import math

from tree_search import *

class PathFinder(SearchDomain):
    def __init__(self, map, rocks, distance, step):
        self.map = map
        self.rocks = rocks
        self.distance = distance
        self.size_x = 47
        self.size_y = 23
        self.step = step
    
    def actions(self, state):
        directions = [
            [state[0], state[1] + 1],
            [state[0], state[1] - 1],
            [state[0] + 1, state[1]],
            [state[0] - 1, state[1]]
        ]
        return directions
    
    def result(self, action):
        return action
    
    def cost(self, action):
        x, y = action
        bad_path = 1000000
        
        # Preventing going outside of the map
        if x > self.size_x or y > self.size_y:
            return bad_path
        
        # Preventing choosing a path with a rock
        for rock in self.rocks:
            if rock.get("pos") == [x,y]:
                return bad_path
        
        if self.distance < 3 and self.step < 1000: # step > 1000: Stuck in horizontal path, ignore tiles/stone cost
            if self.map[x][y] == 0:
                return 5
            else:
                return 20
        else:
            return 0  # greedy search

    def heuristic(self, state, goal):
        x = state[0] - goal[0]
        y = state[1] - goal[1]
        return math.sqrt(x**2 + y**2)

    def satisfies(self, state, goal):
        if state[0] == goal[0] and state[1] == goal[1]:
            return True
        return False