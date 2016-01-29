from __future__ import division # floating point division

import sqlite3
import numpy as np
from collections import namedtuple

conn = sqlite3.connect('../db/universeDataDx.db')
cursor = conn.cursor()

def get_region_id(region):
    cursor.execute('''SELECT regionID FROM mapRegions 
                      WHERE regionName=?''', (region,))
    return cursor.fetchone()[0]

def get_system_ids(region):
    region_id = get_region_id(region)
    cursor.execute('''SELECT solarSystemID from mapSolarSystems
                      WHERE regionID=?''', (region_id,))
    return [res[0] for res in cursor.fetchall()]

def get_system_name(system_id):
    cursor.execute('''SELECT solarSystemName FROM mapSolarSystems 
                      WHERE solarSystemID=?''', (system_id,))
    return cursor.fetchone()[0]

def get_system_id(system_name):
    cursor.execute('''SELECT solarSystemID FROM mapSolarSystems 
                      WHERE solarSystemName=?''', (system_name,))
    return cursor.fetchone()[0]

def get_adjacent_system_pairs(region):
    region_id = get_region_id(region)
    cursor.execute('''SELECT fromSolarSystemID, toSolarSystemID 
                      FROM mapSolarSystemJumps
                      WHERE fromRegionID=? AND toRegionID=?''', 
                   (region_id, region_id))
    return cursor.fetchall()

def get_normalized_ids(ids):
    return { s:i for i,s in enumerate(ids) }

def build_system_adjacency_matrix(region, systems, normalized_system_ids):
    n_systems = len(systems)

    adj_mat = np.full((n_systems, n_systems), np.nan)
    for s1, s2 in get_adjacent_system_pairs(region):
        s1_n = normalized_system_ids[s1]
        s2_n = normalized_system_ids[s2]
        adj_mat[s1_n][s2_n] = 1
        
    return adj_mat

def floyd_apsp(adj_mat):
    n = len(adj_mat[0])
    dist_mat = np.full(adj_mat.shape, np.inf)
    next_mat = np.full(adj_mat.shape, np.nan)

    # initalize dist_mat, next_mat
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

def greedy_ts(dist_mat, next_mat, tour_systems):
    start_system = tour_systems[0]
    destination_system = tour_systems[-1]

    route = [start_system]
    unvisited = set(tour_systems).difference(set(route))

    # Maximize
    def cost(next_system):
        subroute = floyd_path(next_mat, route[-1], next_system)
        new_systems = set(subroute).intersection(unvisited)
        return len(new_systems)/len(subroute)

    while unvisited:
        next_system = max(unvisited, key=cost)
        subroute = floyd_path(next_mat, route[-1], next_system)
        unvisited = unvisited.difference(subroute)
        route.append(next_system)

    return expand_floyd_path(next_mat, route)


# Bounded depth-first-search of solution space
# Feasable for tours with < 60 stops
# Returns [] when no sufficient route is found
def branch_and_bound_ts(next_mat, tour, goal, start, finish):
    SearchState = namedtuple('SearchState', ['route', 'unvisited', 'length'])
    search_stack = [ SearchState([start], set(tour).difference([start]), 1) ]
    
    def visit(search_state, destination):
        subroute = floyd_path(next_mat, search_state.route[-1], destination)
        new_unvisited = search_state.unvisited.difference(subroute)
        new_route = search_state.route + [destination]
        new_length = search_state.length + len(subroute) - 1
        return SearchState(new_route, new_unvisited, new_length)

    def solution(search_state):
        subroute = floyd_path(next_mat, search_state.route[-1], finish)
        new_unvisited = search_state.unvisited.difference(subroute)
        new_length = search_state.length + len(subroute) - 1
        return (new_length <= goal) and (len(new_unvisited) == 0)

    def bound(search_state):
        return search_state.length <= goal

    def branch(search_state):
        for node in search_state.unvisited:
            new_search_state = visit(search_state, node)
            if bound(new_search_state):
                search_stack.insert(0, (new_search_state))
                if solution(new_search_state):
                    return new_search_state

    while search_stack:
        solution_state = branch(search_stack.pop())
        if solution_state:
            return expand_floyd_path(next_mat, solution_state.route + [finish])

    return []

def main():
    region = raw_input()
    start_system = raw_input()
    end_system = raw_input()
    tour = raw_input().split(' ')

    tour = set(tour + [start_system] + [end_system])
    system_ids = get_system_ids(region)

    for system in tour:
        try:
            system_id = get_system_id(system)
        except: 
            print("%s is not a known system" % system)
            return
        if not system_id in system_ids:
            print("%s not found in region (%s)" % (system, region))
            return

    normalized_system_ids = get_normalized_ids(system_ids)
    adj_mat = build_system_adjacency_matrix(region, system_ids, normalized_system_ids)
    dist_mat, next_mat = floyd_apsp(adj_mat)

    normalized_tour_ids = map(lambda x: normalized_system_ids[x], map(get_system_id, tour))
    route = branch_and_bound_ts(next_mat, normalized_tour_ids, 8, 0, 0)

    unnormalized_route = map(lambda x: system_ids[x], route)
    named_route = map(get_system_name, unnormalized_route)

    print(named_route)
    """
    print(len(tour))
    print(len(route))
    """

main()

conn.close()
