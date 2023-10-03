import pandas as pd
import requests
from requests.structures import CaseInsensitiveDict


def add_coordinates(coordId: int, row):
    ### create list for new row in coordinate df
    coordList = [coordId, row["LATITUDE"], row["LONGITUDE"]]
    ### add new row to coordinate df
    coordinates.loc[len(coordinates)] = coordList


def add_addresses(addrId: int, row):
    nameDict = {
        "BOROUGH": "Borough",
        "ZIP CODE": "ZIPCode",
        "ON STREET NAME": "OnStreetName",
        "CROSS STREET NAME": "CrossStreetName",
        "OFF STREET NAME": "OffStreetName"
    }

    ### init dict for new row in address df
    addrDict = {"AddressId": addrId}
    ### iterate over adress fields
    for key in nameDict:
        ### check if field is present
        if not pd.isna(row[key]):
            ### add to new row in address df
            addrDict[nameDict[key]] = row[key]

    if "OffStreetName" in addrDict.keys():
        for x in range(10):
            addrDict["OffStreetName"]=addrDict["OffStreetName"].replace("  "," ")

    ### add new row to address df
    addresses.loc[len(addresses)] = addrDict


def add_timestamps(timeId: int, row):
    allpresent = 0
    ### init dict for new row in timestamp df
    tsDict = {"TimestampId": timeId}
    ### check if date is present
    if not pd.isna(row["CRASH DATE"]):
        ### split date string into list
        dateList = row["CRASH DATE"].split("/")
        ### assign list elements to new row
        tsDict["Month"] = dateList[0]
        tsDict["Day"] = dateList[1]
        tsDict["Year"] = dateList[2]
        allpresent += 1

    ### check if time is present
    if not pd.isna(row["CRASH TIME"]):
        ### assign hour to new row
        tsDict["Hour"] = row["CRASH TIME"].split(":")[0]
        allpresent += 1

    ### if both are present, add full timestamp to new row
    if allpresent == 2:
        tsDict["DateObj"] = f"{tsDict['Year']}-{tsDict['Month']}-{tsDict['Day']} {tsDict['Hour']}:00:00"

    ### add new row to timestamp df
    timestamps.loc[len(timestamps)] = tsDict


###read data
print("reading source file")
data = pd.read_csv("data.csv").head(1000)

###create dataframes for tables
print("creating dataframes")

accidents = pd.DataFrame({
    "CollisionId": pd.Series(dtype="int"),
    "NrVehicles": pd.Series(dtype="int"),
    "NrInjured": pd.Series(dtype="int"),
    "NrKilled": pd.Series(dtype="int"),
    "NrVictims": pd.Series(dtype="int"),
    "TimestampId": pd.Series(dtype="int"),
    "AddressId": pd.Series(dtype="int"),
    "CoordinateId": pd.Series(dtype="int"),
    "ContributingFactorsId": pd.Series(dtype="int"),
    #    "VictimsId":pd.Series(dtype="int"),
    "Vehicle1Id": pd.Series(dtype="int"),
    "Vehicle2Id": pd.Series(dtype="int"),
    "Vehicle3Id": pd.Series(dtype="int"),
    "Vehicle4Id": pd.Series(dtype="int"),
    "Vehicle5Id": pd.Series(dtype="int")
})

coordinates = pd.DataFrame({
    'CoordinateId': pd.Series(dtype='int'),
    'Latitude': pd.Series(dtype='float'), ''
                                          'Longitude': pd.Series(dtype='float')
})

vehicles = pd.DataFrame({
    "VehicleId": pd.Series(dtype="int"),
    #    "ContributingFactor":pd.Series(dtype="str"),
    "Type": pd.Series(dtype="str")

})

timestamps = pd.DataFrame({
    "TimestampId": pd.Series(dtype="int"),
    "Hour": pd.Series(dtype="int"),
    "Day": pd.Series(dtype="int"),
    "Month": pd.Series(dtype="int"),
    "Year": pd.Series(dtype="int"),
    "DateObj": pd.Series(dtype="str")
})

contributingFactors = pd.DataFrame({
    "ContributingFactorsId": pd.Series(dtype="int"),
    "Vehicle1ContributingFactors": pd.Series(dtype="str"),
    "Vehicle2ContributingFactors": pd.Series(dtype="str"),
    "Vehicle3ContributingFactors": pd.Series(dtype="str"),
    "Vehicle4ContributingFactors": pd.Series(dtype="str"),
    "Vehicle5ContributingFactors": pd.Series(dtype="str")
})

# victims = pd.DataFrame({
#    "VictimsId":pd.Series(dtype="int"),
#    "NrInjured":pd.Series(dtype="int"),
#    "NrKilled":pd.Series(dtype="int")
# })

addresses = pd.DataFrame({
    "AddressId": pd.Series(dtype="int"),
    "Borough": pd.Series(dtype="str"),
    "ZIPCode": pd.Series(dtype="int"),
    "OnStreetName": pd.Series(dtype="str"),
    "CrossStreetName": pd.Series(dtype="str"),
    "OffStreetName": pd.Series(dtype="str")
})

### create Indexes
print("creating indexes")
collisionId = 0
coordinateId = 0
vehicleId = 0
timestampId = 0
victimsId = 0
addressId = 0
contributingFactorsId = 0

### iterate over dataframe
print("iterating")
for index, row in data.iterrows():

    ### check for contributing factors and vehicle codes
    noContribFactors = True
    noVehicleTypeCodes = True
    for n in range(1,6):
        if not pd.isna(row[f"VEHICLE TYPE CODE {n}"]):
            noVehicleTypeCodes = False
        if not pd.isna(row[f"CONTRIBUTING FACTOR VEHICLE {n}"]):
            noContribFactors = False

    ### skip current iteration if there are either no contributing factors or no vehicle types
    if noContribFactors or noVehicleTypeCodes:
        continue


    ### create dict for new row in accident df
    rowdict = {"CollisionId": row["COLLISION_ID"], }




    ### check if address is present
    if (
            not pd.isna(row["BOROUGH"]) or
            not pd.isna(row["ZIP CODE"]) or
            not pd.isna(row["ON STREET NAME"]) or
            not pd.isna(row["CROSS STREET NAME"]) or
            not pd.isna(row["OFF STREET NAME"])
    ):
        ### set address id in accidents df
        rowdict["AddressId"] = addressId
        add_addresses(addressId, row)
        ### increment addressId
        addressId += 1

    ### check if timestamp is present
    if (
            not pd.isna(row["CRASH DATE"]) or
            not pd.isna(row["CRASH TIME"])
    ):
        ### set timestamp id in accidents df
        rowdict["TimestampId"] = timestampId
        add_timestamps(timestampId, row)
        ### increment timestampdId
        timestampId += 1

    nrVehicles = 0

    for v in range(1, 6):
        if not pd.isna(row[f"VEHICLE TYPE CODE {v}"]):
            nrVehicles += 1
            vehicleDict = {
                "VehicleId": vehicleId,
                "Type": row[f"VEHICLE TYPE CODE {v}"]
            }
            vehicles.loc[len(vehicles)] = vehicleDict
            rowdict[f"Vehicle{v}Id"] = vehicleId
            vehicleId += 1

    rowdict["NrVehicles"] = nrVehicles

    hasContribFactor = False
    contribFactorsDict = {}
    contribFactorsDict["ContributingFactorsId"] = contributingFactorsId
    for v in range(1, 6):
        if not pd.isna(row[f"CONTRIBUTING FACTOR VEHICLE {v}"]):
            hasContribFactor = True
            contribFactorsDict[f"Vehicle{v}ContributingFactors"] = row[f"CONTRIBUTING FACTOR VEHICLE {v}"]

    if hasContribFactor:
        contributingFactors.loc[len(contributingFactors)] = contribFactorsDict
        rowdict["ContributingFactorsId"] = contributingFactorsId
        contributingFactorsId += 1

    if not pd.isna(row["NUMBER OF PERSONS INJURED"]):
        rowdict["NrInjured"] = row["NUMBER OF PERSONS INJURED"]
    else:
        rowdict["NrInjured"] = 0

    if not pd.isna(row["NUMBER OF PERSONS KILLED"]):
        rowdict["NrKilled"] = row["NUMBER OF PERSONS KILLED"]
    else:
        rowdict["NrKilled"] = 0

    rowdict["NrVictims"] = rowdict["NrInjured"] + rowdict["NrKilled"]

    ### check if coordinates are present
    if (
            not pd.isna(row["LATITUDE"]) and
            not pd.isna(row["LONGITUDE"])
    ):
    ### set coordinate id in accidents df
        rowdict["CoordinateId"] = coordinateId
        add_coordinates(coordinateId, row)
        ### increment coordinateId
        coordinateId += 1


    accidents.loc[len(accidents)] = rowdict


print("done")

### convert Ids to integers
accidents["CollisionId"] = accidents["CollisionId"].astype(int)
accidents["NrVehicles"] = accidents["NrVehicles"].astype(int)
accidents["NrInjured"] = accidents["NrInjured"].astype(int)
accidents["NrKilled"] = accidents["NrKilled"].astype(int)
accidents["NrVictims"] = accidents["NrVictims"].astype(int)
# accidents["NrVictims"] = accidents["NrVictims"].astype(int)
# accidents["TimestampdId"] = accidents["TimestampdId"].astype(int)
# accidents["AdressId"] = accidents["AdressId"].astype(int)
# accidents["CoordinateId"] = accidents["CoordinateId"].astype(int)
# accidents["VictimsId"] = accidents["VictimsId"].astype(int)
# accidents["ContributingFactorsId"] = accidents["ContributingFactors"].astype(int)
# accidents["Vehicle1Id"] = accidents["Vehicle1Id"].astype(int)
# accidents["Vehicle2Id"] = accidents["Vehicle2Id"].astype(int)
# accidents["Vehicle3Id"] = accidents["Vehicle3Id"].astype(int)
# accidents["Vehicle4Id"] = accidents["Vehicle4Id"].astype(int)
# accidents["Vehicle5Id"] = accidents["Vehicle5Id"].astype(int)

coordinates["CoordinateId"] = coordinates["CoordinateId"].astype(int)

vehicles["VehicleId"] = vehicles["VehicleId"].astype(int)

timestamps["TimestampId"] = timestamps["TimestampId"].astype(int)
timestamps["Hour"] = timestamps["Hour"].astype(int)
timestamps["Day"] = timestamps["Day"].astype(int)
timestamps["Month"] = timestamps["Month"].astype(int)
timestamps["Year"] = timestamps["Year"].astype(int)

contributingFactors["ContributingFactorsId"] = contributingFactors["ContributingFactorsId"].astype(int)

# victims["VictimsId"] = victims["VictimsId"].astype(int)
# victims["NrInjured"] = victims["NrInjured"].astype(int)
# victims["NrKilled"] = victims["NrKilled"].astype(int)

addresses["AddressId"] = addresses["AddressId"].astype(int)
# addresses["ZIPCode"] = addresses["ZIPCode"].astype(int)

### save dataframes to csvs
print("saving files")
# print(accidents)
# print(accidents["CoordinateId"])
# print(accidents["AddressId"])
# print(accidents["Vehicle2Id"])
#
# print(addresses)
#
# print(coordinates)
#
# print(timestamps)
#
# print(contributingFactors)
#
# print(vehicles)
#
# print(accidents.loc[4])

#print(addresses["ZIPCode"])

#print(accidents[accidents["NrKilled"] != 0][["NrInjured","NrKilled","NrVictims"]])

accidents.to_csv("accidents.csv", index=False)
addresses.to_csv("addresses.csv", index=False)
coordinates.to_csv("coordinates.csv", index=False)
vehicles.to_csv("vehicles.csv", index=False)
timestamps.to_csv("timestamps.csv", index=False)
contributingFactors.to_csv("contributingFactors.csv", index=False)
