import sqlite3
import numpy as np

# 
# Script to generate SystemsAdjacencyMatrix.csv
# 

conn = sqlite3.connect('../db/universeDataDx.db')

systems = [res[0] for res in conn.execute('''SELECT solarSystemID from mapSolarSystems 
                                             ORDER BY solarSystemID''')]

NUM_SYSTEMS = len(systems)

# Maps normalized system ids to actual system ids
system_indices = { s:i for i,s in enumerate(systems) }

systems_adj_mat = np.zeros((NUM_SYSTEMS, NUM_SYSTEMS))

# Populate systems adjacency matrix
for res in conn.execute('SELECT * from mapSolarSystemJumps'):
    s1_i = system_indices[res[2]]
    s2_i = system_indices[res[3]]
    systems_adj_mat[s1_i][s2_i] = 1

np.savetxt("SystemsAdjacencyMatrix.csv", systems_adj_mat, fmt='%i', delimiter=',')

