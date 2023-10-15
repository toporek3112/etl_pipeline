import psycopg2
import pandas as pd
import re
import sys

print("Setup Database Connection")
conn = psycopg2.connect(
   database="postgres", user='postgres', password='password', host='localhost', port= '5432'
)
conn.autocommit=False
cursor = conn.cursor()

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

    return f'insert into \"{table}\" ({sqlKeys}) VALUES ({sqlValues});'

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




contributingFactorIds = [0,0,0,0,0]
cursor.execute('SELECT max("ContributingFactorId") FROM "ContributingFactors";')
contributingfactorId=cursor.fetchone()[0]
if contributingfactorId != None:
    contributingfactorId = contributingfactorId+1
else:
    contributingfactorId = 0

contributingFactorCorrection={}
contributingFactorCodes=pd.read_csv("data/contributingFactorsCorrection.csv")
for index, row in contributingFactorCodes.iterrows():
    if not pd.isna(row["correctFactor"]):
        contributingFactorCorrection[row["factor"]]=row["correctFactor"]
    else:
        contributingFactorCorrection[row["factor"]] = "Unspecified"


vehicleIds = [0,0,0,0,0]
cursor.execute('SELECT max("VehicleId") FROM "Vehicles";')
vehicleId=cursor.fetchone()[0]
if vehicleId!=None:
    vehicleId = vehicleId+1
else:
    vehicleId=0

vehicleCorrection={}
vehicleCodes=pd.read_csv("data/vehicleCodesCorrection.csv")
for index, row in vehicleCodes.iterrows():
    if not pd.isna(row["correctCode"]):
         vehicleCorrection[row["code"]]=row["correctCode"]
    else:
        vehicleCorrection[row["code"]] = "Unknown"




print("Checking total amount of data:")
cursor.execute('SELECT count(collision_id) FROM "Staging";')
max=cursor.fetchone()[0]
cursor.execute('SELECT max("AccidentId") FROM "Accidents";')
min=cursor.fetchone()[0]
query_size=10000
lower_bound=0
if min!=None:
    lower_bound=min+1
upper_bound= (max - max % query_size) + query_size + 1
#upper_bound=1000

cursor.execute('SELECT max("TimestampId") FROM "Timestamps";')
tsMax=cursor.fetchone()[0]
cursor.execute('SELECT max("CoordinateId") FROM "Coordinates";')
coordMax=cursor.fetchone()[0]
cursor.execute('SELECT max("AddressId") FROM "Addresses";')
addrMax=cursor.fetchone()[0]

timestampId = tsMax+1 if tsMax != None else 0
coordinateId = coordMax+1 if coordMax != None else 0
addressId = addrMax+1 if addrMax != None else 0
accidentId = lower_bound


print(f"found {max} rows")
print("Starting Requests")
select="crash_date,crash_time,latitude,longitude,borough,zip_code,on_street_name,off_street_name,cross_street_name,number_of_persons_injured,number_of_persons_killed,number_of_pedestrians_injured,number_of_pedestrians_killed,number_of_cyclist_injured,number_of_cyclist_killed,number_of_motorist_injured,number_of_motorist_killed,contributing_factor_vehicle_1,contributing_factor_vehicle_2,contributing_factor_vehicle_3,contributing_factor_vehicle_4,contributing_factor_vehicle_5,collision_id,vehicle_type_code_1,vehicle_type_code_2,vehicle_type_code_3,vehicle_type_code_4,vehicle_type_code_5"
for bound in range(lower_bound, upper_bound, query_size):
    print(f"Querying entries {bound} to {bound + query_size}")
    cursor.execute(f'SELECT {select} FROM "Staging" LIMIT {query_size} OFFSET {bound};')
    results=cursor.fetchall()
    #17-21: Contributing Factors, 23-27: Vehicle Codes
    #print(results[0])
    print("Inserting into Databases:")
    for result in results:
        progress_bar(results.index(result), len(results))
        if re.match("\\d+",str(result[5])):
            accidentDict={"AccidentId":accidentId,"CollisionId":result[22]}
            insert_timestamp(timestampId,result)
            insert_coordinates(coordinateId,result)
            insert_address(addressId,result)
            contributingFactorIds,contributingfactorId = insert_contributing_factors(contributingfactorId,result)

            vehicleIds,vehicleId, nrVehicles = insert_vehicles(vehicleId,result)
            for n in range(5):
                if contributingFactorIds[n]!= None:
                    accidentDict[f'ContributingFactor{n+1}Id']=contributingFactorIds[n]
                if vehicleIds[n] != None:
                    accidentDict[f'Vehicle{n+1}Id']=vehicleIds[n]
            accidentDict["NrVehicles"] = nrVehicles
            if result[9]!=None:
                accidentDict["NrInjured"]=int(result[9])
            else:
                accidentDict["NrInjured"] = 0
            if result[10] != None:
                accidentDict["NrKilled"]=int(result[10])
            else:
                accidentDict["NrKilled"] = 0

            accidentDict["NrVictims"]=accidentDict["NrInjured"]+accidentDict["NrKilled"]
            accidentDict["TimestampId"] = timestampId
            accidentDict["CoordinateId"] = coordinateId
            accidentDict["AddressId"] = addressId

            cursor.execute(generate_insert_string("Accidents",accidentDict))
            conn.commit()

            coordinateId += 1
            timestampId += 1
            addressId += 1
            accidentId += 1
    print(f'\n{round(((bound-lower_bound)/(upper_bound-lower_bound))*100)}% Done')


print("Done")






