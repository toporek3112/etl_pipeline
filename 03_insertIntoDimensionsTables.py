import psycopg2
import pandas as pd
import re
import sys
import json
import csv

with open('db_config.json', 'r') as file:
    config = json.load(file)

STAGING_TABLE_NAME=config['staging_table_name']
DATABASE_SETTINGS = config['database_settings']

def setup_db_connection():
    print("Setup Database Connection")
    conn = psycopg2.connect(**DATABASE_SETTINGS)
    conn.autocommit = False
    cursor = conn.cursor()
    return conn, cursor

def progress_bar(cur_index:int,total:int):
    percent = round((cur_index+1) / total * 100)
    prog = round(percent/5)
    sys.stdout.write('\r')
    sys.stdout.write('['+'='*prog+'.'*(20-prog)+f'] {percent}%')
    sys.stdout.flush()

def generate_insert_string(table:str,contents:dict):
    sqlKeys = ""
    sqlValues = ""
    for k in contents.keys():
        if sqlKeys == "":
            sqlKeys = f'"{k}"'
        else:
            sqlKeys = sqlKeys + f',"{k}"'

    for v in contents.values():
        if sqlValues == '':
            sqlValues = "'" + str(v).replace("'", "''") + "'"
        else:
            sqlValues = sqlValues + ",'" + str(v).replace("'", "''") + "'"

    return f'insert into "{table}" ({sqlKeys}) VALUES ({sqlValues});'

def insert_coordinates(coordId,result):
    coordDict={"CoordinateId":coordId}
    coordDict["Latitude"] = result[2]
    coordDict["Longitude"] = result[3]
    cursor.execute(generate_insert_string("Coordinates", coordDict))
    conn.commit()

def insert_timestamp(timeId, result):
    tsDict = {"TimestampId": timeId}

    dateStr=str(result[0])

    ### split date string into list
    dateList = dateStr.split("-")
    ### assign list elements to new row
    tsDict["Month"] = dateList[1]
    tsDict["Day"] = dateList[2]
    tsDict["Year"] = dateList[0]
    tsDict["Hour"] = result[1].split(":")[0]
    tsDict["DateObj"] = f'{tsDict["Year"]}-{tsDict["Month"]}-{tsDict["Day"]}T{tsDict["Hour"]}:00:00.0000'
    cursor.execute(generate_insert_string("Timestamps", tsDict))
    conn.commit()

def insert_address(addrId, result):
    addrDict = {"AddressId": addrId}
    addrkeys=["Borough","OnStreetName","OffStreetName","CrossStreetName"]
    if result[4] != None:
        addrDict["Borough"] = str(result[4]).strip()
    addrDict["ZIPCode"] = int(result[5])
    if result[6] != None:
        addrDict["OnStreetName"] = str(result[6]).strip()
    if result[7] != None:
        addrDict["OffStreetName"] = str(result[7]).strip()
    if result[8] != None:
        addrDict["CrossStreetName"] = str(result[8]).strip()
    cursor.execute(generate_insert_string("Addresses", addrDict))
    conn.commit()

def insert_contributing_factors(contributingfactorId,result):
    contributingfactors=list(result[17:22])
    res=[None,None,None,None,None]
    for factor in contributingfactors:
        if factor!=None:
            correctFactor = contributingFactorCorrection[factor]
            cursor.execute(f'SELECT "ContributingFactorId" FROM "ContributingFactors" WHERE "ContributingFactor" = \'{correctFactor}\'')
            id=cursor.fetchone()
            if id == None:
                cursor.execute(f'INSERT INTO "ContributingFactors" ("ContributingFactorId", "ContributingFactor") VALUES (\'{contributingfactorId}\',\'{correctFactor}\')')
                conn.commit()
                id=contributingfactorId
                contributingfactorId += 1
            else:
                id=id[0]
            res[contributingfactors.index(factor)] = id
    return res, contributingfactorId

def insert_vehicles(vehicleId,result):
    vehicles = list(result[23:28])
    res = [None, None, None, None, None]
    nr=0
    for vehicle in vehicles:
        if vehicle!=None:
            nr += 1
            correctVehicle=vehicleCorrection[vehicle]
            cursor.execute(f'SELECT "VehicleId" FROM "Vehicles" WHERE "Type" = \'{correctVehicle}\'')
            id = cursor.fetchone()
            if id == None:
                cursor.execute(f'INSERT INTO "Vehicles" ("VehicleId", "Type") VALUES (\'{vehicleId}\',\'{correctVehicle}\')')
                conn.commit()
                id = vehicleId
                vehicleId += 1
            else:
                id=id[0]
            res[vehicles.index(vehicle)] = id
        return res, vehicleId, nr



def correct(corrections_df):
    corrected_values = []  # Initialize an empty list
    
    for index, row in corrections_df.iterrows():  # Iterate through DataFrame rows
        if pd.isnull(row['corrected']) or row['corrected'] == '':  # Check if 'corrected' value is null or empty
            corrected_values.append(row['original'])  # Use 'original' value
        else:
            corrected_values.append(row['corrected'])  # Use 'corrected' value
    
    corrected_series = pd.Series(corrected_values)  # Convert list to Series
    corrected_series = corrected_series.drop_duplicates().reset_index(drop=True)  # Remove duplicates and reset index
    
    return corrected_series

def truncate_dimension(cursor, table_name):
    query = f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;"
    try:
        cursor.execute(query)
        print(f"Successfully truncated the {table_name} table and reset its identity column.")
    except Exception as e:
        print(f"An error occurred: {e}")

def insert_into_dimension(cursor, table_name, columns, data_series):
    truncate_dimension(cursor, table_name)
    print(f"Inserting into dimension table {table_name}")

    # Convert the pandas Series to a list of tuples, each containing one value
    data = [(value,) for value in data_series]

    # Create a string of placeholders for the values
    placeholders = ', '.join(['%s'] * len(columns))

    # Create the SQL query string
    query = f"""
        INSERT INTO {table_name} ({', '.join(columns)})
        VALUES ({placeholders})
        ON CONFLICT DO NOTHING  -- This line is optional, to ignore duplicate entries
    """

    try:
        # Log the data and query for debugging
        print(f"Query: {query}")
        print(f"Data: {data}")

        # Execute the query with the data
        cursor.executemany(query, data)
        print(f"Successfully inserted {len(data)} rows into {table_name}")

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    conn, cursor = setup_db_connection()
    print("")
    
    contributing_factors = pd.read_csv("data/stagingContributingFactorsCorrected.csv")
    contributing_factors_corrected = correct(contributing_factors)

    columns = ["contributing_factor"]
    insert_into_dimension(cursor, "dim_contributing_factors", columns, contributing_factors_corrected)

    vehicles = pd.read_csv("data/stagingVehicleTypesCorrected.csv")
    vehicles_corrected = correct(vehicles)
    print("")

    columns = ["vehicle_type"]
    insert_into_dimension(cursor, "dim_vehicles", columns, vehicles_corrected)


    conn.commit()  # Commit the transaction

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
