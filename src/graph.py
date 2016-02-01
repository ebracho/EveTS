from __future__ import division # floating point division
import numpy as np
from collections import deque, namedtuple
from setdeque import SetDeque

def build_adjacency_matrix(n_nodes, edges):
    adj_mat = np.full((n_nodes, n_nodes), np.nan)
    for n1, n2 in edges:
        adj_mat[n1][n2] = 1
    return adj_mat

def floyd_apsp(adj_mat):
    n = len(adj_mat[0])
    dist_mat = np.full(adj_mat.shape, np.inf)
    next_mat = np.full(adj_mat.shape, np.nan)

    # Initalize dist_mat, next_mat
    for i in range(n):
        for j in range(n): 
            if not np.isnan(adj_mat[i][j]):
                dist_mat[i][j] = adj_mat[i][j]
                next_mat[i][j] = j

    # Find shortest path between all pairs
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist_mat[i][k] + dist_mat[k][j] < dist_mat[i][j]:
                    dist_mat[i][j] = dist_mat[i][k] + dist_mat[k][j]
                    next_mat[i][j] = next_mat[i][k]

    return dist_mat.astype(np.int), next_mat.astype(np.int)

def floyd_path(next_mat, u, v): 
    if np.isnan(next_mat[u][v]):
        return []
    path = [u]
    while u != v:
        u = next_mat[u][v]
        path.append(u)
    return path

def expand_floyd_path(next_mat, path): 
    def f(u,v): 
        if type(u) is list:
            s1 = u[-1]
        else:
            s1 = u
            u = [u]
        return u[:-1] + floyd_path(next_mat, s1, v)
    return reduce(f, path)

def greedy_ts(next_mat, tour):
    if not tour: 
        return []

    route = [tour.pop()]
    unvisited = set(tour).difference(set(route))

    # Maximize
    def cost(next_system):
        subroute = floyd_path(next_mat, route[-1], next_system)
        new_systems = set(subroute).intersection(unvisited)
        return len(new_systems)/len(subroute)

    while unvisited:
        next_node = max(unvisited, key=cost)
        subroute = floyd_path(next_mat, route[-1], next_node)
        unvisited = unvisited.difference(subroute)
        route.append(next_system)

    return expand_floyd_path(next_mat, route)

# Bounded breadth-first-search of solution space
# Feasable for tours with < 60 stops
# Returns [] when no sufficient route is found
def branch_and_bound_ts(next_mat, tour, goal, start, finish):
    SearchState = namedtuple('SearchState', ['route', 'unvisited', 'length'])
    search_queue = SetDeque([SearchState((start,), frozenset(tour).difference([start]), 1)])

    def visit(search_state, destination):
        subroute = floyd_path(next_mat, search_state.route[-1], destination)
        new_unvisited = search_state.unvisited.difference(subroute)
        new_route = search_state.route + (destination,)
        new_length = search_state.length + len(subroute) - 1
        return SearchState(new_route, new_unvisited, new_length)

    def solution(search_state):
        route = visit(search_state, finish)
        return (route.length <= goal) and (len(route.unvisited) == 0)

    def bound(search_state):
        return search_state.length <= goal

    def branch(search_state):
        for node in search_state.unvisited:
            new_search_state = visit(search_state, node)
            if bound(new_search_state):
                search_queue.append(new_search_state)
                if solution(new_search_state):
                    return new_search_state

    while search_queue:
        solution_state = branch(search_queue.pop())
        if solution_state:
            return expand_floyd_path(next_mat, solution_state.route + (finish,))

    return []

