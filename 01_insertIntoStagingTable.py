import psycopg2
from sodapy import Socrata
import sys
import json

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

def setup_api_connection():
    print('Setup API connection')
    return Socrata("data.cityofnewyork.us", "mZ2a4QZWgW1U6H36nLENWBkuE")

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

def main():
    conn, cursor = setup_db_connection()
    client = setup_api_connection()
    total = 0

    print("Checking total amount of data:")
    rows_count = int(client.get("h9gi-nx95", select='max(collision_id)')[0]["max_collision_id"])
    request_size = 20000
    cursor.execute(f'SELECT MAX(collision_id) FROM {STAGING_TABLE_NAME};')
    dbRes = cursor.fetchone()[0]
    lower_bound = dbRes+1 if dbRes is not None else 0
    upper_bound = (rows_count - rows_count % request_size) + request_size + 1

    print(f"found {rows_count} rows")
    print("Starting Requests")

    select = 'crash_date,crash_time,borough,zip_code,latitude,longitude,on_street_name,cross_street_name,off_street_name,number_of_persons_injured,number_of_persons_killed,number_of_pedestrians_injured,number_of_pedestrians_killed,number_of_cyclist_injured,number_of_cyclist_killed,number_of_motorist_injured,number_of_motorist_killed,contributing_factor_vehicle_1,contributing_factor_vehicle_2,contributing_factor_vehicle_3,contributing_factor_vehicle_4,contributing_factor_vehicle_5,collision_id,vehicle_type_code1 as vehicle_type_code_1,vehicle_type_code2 as vehicle_type_code_2,vehicle_type_code_3,vehicle_type_code_4,vehicle_type_code_5'
    for bound in range(lower_bound, upper_bound, request_size):
        print(f'requesting id {bound} to {bound + request_size} from {rows_count}')
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
        progress_bar(lower_bound + total, rows_count)
        print('')

    print(f"sum: {total}")

if __name__ == "__main__":
    main()