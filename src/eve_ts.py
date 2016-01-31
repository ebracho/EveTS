from universe_queries import *
from graph import *

def get_normalized_ids(ids):
    return { s:i for i,s in enumerate(ids) }

def main():
    region = raw_input()
    start_system = raw_input()
    end_system = raw_input()
    tour = raw_input().split('|')
    goal = int(raw_input())

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

    # Map to normalized universe data
    normalized_systems = get_normalized_ids(system_ids)

    normalized_start_system = normalized_systems[get_system_id(start_system)]
    normalized_end_system = normalized_systems[get_system_id(end_system)]

    normalized_edges = [ (normalized_systems[s1], normalized_systems[s2]) 
                          for s1, s2 in get_adjacent_system_pairs(region) ]

    normalized_tour_ids = map(lambda x: normalized_systems[x], 
                              map(get_system_id, tour))

    # Compute route
    adj_mat = build_adjacency_matrix(len(normalized_systems), normalized_edges)
    dist_mat, next_mat = floyd_apsp(adj_mat)

    route = branch_and_bound_ts(next_mat, normalized_tour_ids, goal, 
                                normalized_start_system, normalized_end_system)

    # Map back to unnormalized system data
    unnormalized_route = map(lambda x: system_ids[x], route)
    named_route = map(get_system_name, unnormalized_route)

    for system in named_route:
        print(system + ('*' if system in tour else ''))


if __name__ == '__main__':
    main()
