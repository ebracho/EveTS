import sqlite3
import numpy as np

conn = sqlite3.connect('../db/universeDataDx.db')
cursor = conn.cursor()

def get_region_id(region):
    cursor.execute("""SELECT regionID FROM mapRegions 
                      WHERE regionName=?""", (region,))
    return cursor.fetchone()[0]

def get_systems(region):
    region_id = get_region_id(region)
    cursor.execute("""SELECT solarSystemID from mapSolarSystems
                      WHERE regionID=?""", (region_id,))
    return [res[0] for res in cursor.fetchall()]

def get_adjacent_system_pairs(region):
    region_id = get_region_id(region)
    cursor.execute("""SELECT fromSolarSystemID, toSolarSystemID 
                      FROM mapSolarSystemJumps
                      WHERE fromRegionID=? AND toRegionID=?""", 
                   (region_id, region_id))
    return cursor.fetchall()

def build_system_adjacency_matrix(region):
    systems = get_systems(region)
    normalized_system_ids = { s:i for i,s in enumerate(systems) }
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

adj_mat = build_system_adjacency_matrix('The Bleak Lands')
dist_mat, next_mat = floyd_apsp(adj_mat)
print(floyd_path(next_mat, 1, 4))

conn.close()
