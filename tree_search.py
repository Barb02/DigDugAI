# Students:
# Bárbara Nóbrega Galiza - 105937
# Pedro Daniel Fidalgo de Pinho - 109986

"""
    Using a somewhat modified version of the tree_search provided to us
    during the practical classes
    
    Credit :
   (c) Luis Seabra Lopes
   Introducao a Inteligencia Artificial, 2012-2019,
   Inteligência Artificial, 2014-2019
"""

from abc import ABC, abstractmethod
import time

class SearchDomain(ABC):

    # construtor
    @abstractmethod
    def __init__(self):
        pass

    # lista de accoes possiveis num estado
    @abstractmethod
    def actions(self, state):
        pass

    # resultado de uma accao num estado, ou seja, o estado seguinte
    @abstractmethod
    def result(self, action):
        pass

    # custo de uma accao num estado
    @abstractmethod
    def cost(self, action):
        pass

    # custo estimado de chegar de um estado a outro
    @abstractmethod
    def heuristic(self, state, goal):
        pass

    # test if the given "goal" is satisfied in "state"
    @abstractmethod
    def satisfies(self, state, goal):
        pass


class SearchProblem:
    def __init__(self, domain, initial, goal):
        self.domain = domain
        self.initial = initial
        self.goal = goal

    def goal_test(self, state):
        return self.domain.satisfies(state,self.goal)


class SearchNode:
    def __init__(self, state, parent, depth, cost, heuristic): 
        self.state = state
        self.parent = parent
        self.depth = depth
        self.cost = cost
        self.heuristic = heuristic

    def in_parent(self, newstate):

        if(self.state[0] == newstate[0] and self.state[1] == newstate[1]):
            return True
        if(self.parent == None): # é a root
            return False
        
        return self.parent.in_parent(newstate)

    def __str__(self):
        return "no(" + str(self.state) + "," + str(self.parent) + ")"
    
    def __repr__(self):
        return str(self)


class SearchTree:

    def __init__(self,problem): 
        self.problem = problem
        root = SearchNode(problem.initial, None, 0, 0, problem.domain.heuristic(problem.initial, problem.goal))
        self.open_nodes = [root]
        self.solution = None
        self.non_terminals = 0
        self._total_depth = 0
        self.start_time = round(time.time() * 1000)

    # obter o caminho (sequencia de estados) da raiz ate um no
    def get_path(self,node):
        if node.parent == None:
            return [node.state]
        path = self.get_path(node.parent)
        path += [node.state]
        return(path)

    # procurar a solucao
    def search(self, limit = None):
        while self.open_nodes != []:

            node = self.open_nodes.pop(0)

            if self.problem.goal_test(node.state):
                self.solution = node
                return self.get_path(node)
            
            self.non_terminals += 1

            lnewnodes = []
            for a in self.problem.domain.actions(node.state):
                if self.start_time + 300 < round(time.time() * 1000):
                    return None
                newstate = self.problem.domain.result(a)

                if not node.in_parent(newstate) and (limit == None or node.depth < limit):
                    cost = node.cost + self.problem.domain.cost(a)
                    heuristic = self.problem.domain.heuristic(newstate, self.problem.goal)
                    newnode = SearchNode(newstate,node, node.depth + 1, cost, heuristic)
                    lnewnodes.append(newnode)
                    self._total_depth += newnode.depth

            self.add_to_open(lnewnodes)

        return None

    # juntar novos nos a lista de nos abertos
    def add_to_open(self,lnewnodes):
        self.open_nodes.extend(lnewnodes)
        self.open_nodes.sort(key = lambda x : x.heuristic + x.cost)

