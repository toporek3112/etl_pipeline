import psycopg2
import pandas as pd
from sodapy import Socrata
import sys

STAGING_TABLE_NAME="staging_02"
DATABASE_SETTINGS = {
    "database": "postgres",
    "user": "postgres",
    "password": "password",
    "host": "localhost",
    "port": "5432"
}

def progress_bar(cur_index: int, total: int):
    percent = round((cur_index + 1) / total * 100)
    prog = round(percent / 5)
    sys.stdout.write('\r')
    sys.stdout.write('['+'='*prog+'.'*(20-prog)+f'] {percent}%')
    sys.stdout.flush()

def insert_to_staging(cursor, results, staging_table_name: str):
    expected_columns = [
        'crash_date', 'crash_time', 'borough', 'zip_code', 'latitude', 'longitude', 
        'on_street_name', 'off_street_name', 'number_of_persons_injured', 
        'number_of_persons_killed', 'number_of_pedestrians_injured', 
        'number_of_pedestrians_killed', 'number_of_cyclist_injured', 
        'number_of_cyclist_killed', 'number_of_motorist_injured', 
        'number_of_motorist_killed', 'contributing_factor_vehicle_1',
        'contributing_factor_vehicle_2', 'contributing_factor_vehicle_3',
        'contributing_factor_vehicle_4', 'contributing_factor_vehicle_5', 
        'collision_id', 'vehicle_type_code_1', 'vehicle_type_code_2', 
        'vehicle_type_code_3', 'vehicle_type_code_4', 'vehicle_type_code_5',
        'cross_street_name'
    ]

    placeholders = ', '.join(['%s'] * len(expected_columns))
    columns = ', '.join(expected_columns)
    data = [tuple(item.get(col, None) for col in expected_columns) for item in results]
    query = f'INSERT INTO {staging_table_name} ({columns}) VALUES ({placeholders})'
    cursor.executemany(query, data)

print('Setup API connection')
client = Socrata("data.cityofnewyork.us", "mZ2a4QZWgW1U6H36nLENWBkuE")

print("Setup Database Connection")
conn = psycopg2.connect(database="postgres", user='postgres', password='password', host='localhost', port='5432')
conn.autocommit = False
cursor = conn.cursor()

data = pd.DataFrame()
total = 0

print("Checking total amount of data:")
rows_count = int(client.get("h9gi-nx95", select='max(collision_id)')[0]["max_collision_id"])
request_size = 10000
cursor.execute(f'SELECT MAX(collision_id) FROM {STAGING_TABLE_NAME};')
lower_bound = cursor.fetchone()[0]+1
upper_bound = (rows_count - rows_count % request_size) + request_size + 1

print(f"found {rows_count} rows")
print("Starting Requests")

select = 'crash_date,crash_time,borough,zip_code,latitude,longitude,on_street_name,cross_street_name,off_street_name,number_of_persons_injured,number_of_persons_killed,number_of_pedestrians_injured,number_of_pedestrians_killed,number_of_cyclist_injured,number_of_cyclist_killed,number_of_motorist_injured,number_of_motorist_killed,contributing_factor_vehicle_1,contributing_factor_vehicle_2,contributing_factor_vehicle_3,contributing_factor_vehicle_4,contributing_factor_vehicle_5,collision_id,vehicle_type_code1 as vehicle_type_code_1,vehicle_type_code2 as vehicle_type_code_2,vehicle_type_code_3,vehicle_type_code_4,vehicle_type_code_5'
for bound in range(lower_bound, upper_bound, request_size):
    print(f'requesting id {bound} to {bound + request_size}')
    where = (
        f'collision_id >= {bound} and collision_id < {bound+request_size} and ('
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
    
    results = client.get("h9gi-nx95", limit=request_size, where=where, select=select)
    total += len(results)
    
    print(f'found {len(results)} results')
    print('Writing to Staging Database')
    
    insert_to_staging(cursor, results, STAGING_TABLE_NAME)
    conn.commit()
    
    # print(f'\n{round(bound / upper_bound * 100)}% Done')
    progress_bar(total, rows_count)
    print('')

    data = pd.concat([data, pd.DataFrame(results)], ignore_index=True)

print(f"sum: {total}")
print('datatypes:')
print(data.dtypes)

if not data.empty:
    contributingFactors = []
    vehicleCodes = []
    for n in range(1, 6):
        contributingFactors.extend([factor for factor in data[f'contributing_factor_vehicle_{n}'].unique() if factor not in contributingFactors])
        vehicleCodes.extend([code for code in data[f'vehicle_type_code_{n}'].unique() if code not in vehicleCodes])

    print("Contributing factors:")
    print(contributingFactors)
    print("Vehicle codes:")
    print(vehicleCodes)

    with open(r'data/contributingFactors.txt', 'w') as fp:
        fp.write('\n'.join(map(str, contributingFactors)))
    
    with open(r'data/vehicleCodes.txt', 'w') as fp:
        fp.write('\n'.join(vehicleCodes))
    
    with open(r'data/columns.sql', 'w') as fp:
        for col in data.columns:
            fp.write(f'alter table "Staging" add {col};\n')