import sqlite3

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

