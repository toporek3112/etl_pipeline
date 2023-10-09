import psycopg2
import pandas as pd
from sodapy import Socrata
import sys

def progress_bar(cur_index:int,total:int):
    percent = round((cur_index+1) / total * 100)
    prog = round(percent/5)
    sys.stdout.write('\r')
    sys.stdout.write('['+'='*prog+'.'*(20-prog)+f'] {percent}%')
    sys.stdout.flush()


print("Setup API connection")
client = Socrata("data.cityofnewyork.us", "mZ2a4QZWgW1U6H36nLENWBkuE")

print("Setup Database Connection")
conn = psycopg2.connect(
   database="postgres", user='postgres', password='password', host='localhost', port= '5432'
)
conn.autocommit=False
cursor = conn.cursor()


data=pd.DataFrame()
total=0

print("Checking total amount of data:")
max = int(client.get("h9gi-nx95", select='max(collision_id)')[0]["max_collision_id"])
upper_bound=(max-max%2000)+2001
print(f"found {max} rows")
print("Starting Requests")
select = 'crash_date,crash_time,borough,zip_code,latitude,longitude,on_street_name,off_street_name,number_of_persons_injured,number_of_persons_killed,number_of_pedestrians_injured,number_of_pedestrians_killed,number_of_cyclist_injured,number_of_cyclist_killed,number_of_motorist_injured,number_of_motorist_killed,contributing_factor_vehicle_1,contributing_factor_vehicle_2,contributing_factor_vehicle_3,contributing_factor_vehicle_4,contributing_factor_vehicle_5,collision_id,vehicle_type_code1 as vehicle_type_code_1,vehicle_type_code2 as vehicle_type_code_2,vehicle_type_code_3,vehicle_type_code_4,vehicle_type_code_5,cross_street_name'
for bound in range(0,upper_bound,2000):
#for bound in range(0,10001,2000):
    where = (
        f'collision_id >= {bound} and collision_id < {bound+2000} and ('
        'contributing_factor_vehicle_1 != "Unspecified" or '
        'contributing_factor_vehicle_2 != "Unspecified" or '
        'contributing_factor_vehicle_3 != "Unspecified" or '
        'contributing_factor_vehicle_4 != "Unspecified" or '
        'contributing_factor_vehicle_5 != "Unspecified" )  and ('
        'vehicle_type_code1 != "UNKNOWN" or '
        'vehicle_type_code2 != "UNKNOWN" or '
        'vehicle_type_code_3 != "UNKNOWN" or '
        'vehicle_type_code_4 != "UNKNOWN" or '
        'vehicle_type_code_5 != "UNKNOWN") and '
        'latitude != 0 and longitude != 0'
             )
    #print(select)

    #print(where)
    print(f'requesting id {bound} to {bound+2000}')
    results = client.get("h9gi-nx95", limit=2000,where=where,select=select)
    #print(type(results))
    #print(type(results[0]))
    total += len(results)
    print(f'found  {len(results)} results')
    print('Writing to Staging Database')
    for result in results:
        progress_bar(results.index(result),len(results))
        sqlKeys=""
        sqlValues=""
        for k in result.keys():
            if sqlKeys=="":
                sqlKeys=k
            else:
                sqlKeys = sqlKeys + f',{k}'

        for v in result.values():
            if sqlValues=='':
                sqlValues=f"'{v}'"
            else:
                sqlValues = sqlValues + f",'{v}'"

        sqlstr=f'insert into "Staging" ({sqlKeys}) VALUES ({sqlValues});'
        #print(sqlstr)
        cursor.execute(sqlstr)
        conn.commit()
    print('\nDone')

    data=pd.concat([data,pd.DataFrame(results)],ignore_index=True)

print(f"sum: {total}")
print('datatypes:')
print(data.dtypes)
data = data.rename({'vehicle_type_code1': 'vehicle_type_code_1', 'vehicle_type_code2': 'vehicle_type_code_2'}, axis=1)

contributingFactors=[]
vehicleCodes=[]
for n in range(1,6):
    for contributingFactor in list(data[f'contributing_factor_vehicle_{n}'].value_counts().index):
        if contributingFactor not in contributingFactors:
            contributingFactors.append(contributingFactor)
    for vehicleCode in list(data[f'vehicle_type_code_{n}'].value_counts().index):
        if vehicleCode not in vehicleCodes:
            vehicleCodes.append(vehicleCode)

print("Contributing factors:")
print(contributingFactors)
print("Vehicle codes:")
print(vehicleCodes)

with open(r'data/contributingFactors.txt', 'w') as fp:
    print('Writing contributingFactors.txt')
    for contFactor in contributingFactors:
        # write each item on a new line
        fp.write("%s\n" % contFactor)
    print('Done')

with open(r'data/vehicleCodes.txt', 'w') as fp:
    print('Writing vehicleCodes.txt')
    for vehCode in vehicleCodes:
        # write each item on a new line
        fp.write("%s\n" % vehCode)
    print('Done')

with open(r'data/columns.sql','w') as fp:
    print('Writing columns.sql')
    for col in data.columns:
        str=f'alter table "Staging" add {col};\n'
        fp.write(str)
    print('Done')



