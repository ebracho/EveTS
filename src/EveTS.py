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

    adj_mat = np.zeros((n_systems, n_systems))
    for s1, s2 in get_adjacent_system_pairs(region):
        s1_n = normalized_system_ids[s1]
        s2_n = normalized_system_ids[s2]
        adj_mat[s1_n][s2_n] = 1
        
    return adj_mat

conn.close()
