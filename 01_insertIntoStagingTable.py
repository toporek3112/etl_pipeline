import sys
import json
from sodapy import Socrata
from utils.time_decorator import timer
from utils.database import setup_db_connection, DB_CONFIG

def setup_api_connection():
    print('Setup API connection...')
    return Socrata("data.cityofnewyork.us", "mZ2a4QZWgW1U6H36nLENWBkuE")

def progress_bar(cur_index: int, total: int):
    percent = round((cur_index + 1) / total * 100)
    prog = round(percent / 5)
    sys.stdout.write('\r')
    sys.stdout.write('['+'='*prog+'.'*(20-prog)+f'] {percent}%')
    sys.stdout.flush()

def cleanup_data(results):
    cleanup_data = []
    for row in results:
        for key, value in row.items():
            if isinstance(value, str):
                row[key] = value.strip()

        # Convert numerical fields to actual number types (int or float)
        numeric_fields = [
            'latitude', 'longitude', 'number_of_persons_injured', 'number_of_persons_killed',
            'number_of_pedestrians_injured', 'number_of_pedestrians_killed',
            'number_of_cyclist_injured', 'number_of_cyclist_killed',
            'number_of_motorist_injured', 'number_of_motorist_killed', 'collision_id'
        ]

        for field in numeric_fields:
            field_value = row.get(field)
            if field_value is not None:
                if '.' in field_value:  # Convert to float if it has a decimal point
                    row[field] = float(field_value)
                else:
                    row[field] = int(field_value)

        # Handle special cases for certain fields
        if row.get('zip_code') is None:
            row['zip_code'] = '-1'

        cleanup_data.append(row)
    
    return cleanup_data

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

@timer
def main():
    conn, cursor = setup_db_connection()
    client = setup_api_connection()
    total = 0

    print("")
    print("Checking total amount of data:")
    api_max_collision_id = int(client.get("h9gi-nx95", select='max(collision_id)')[0]["max_collision_id"])
    request_size = 20000
    cursor.execute(f"SELECT MAX(collision_id) FROM {DB_CONFIG.TABLE_NAMES['STAGING_TABLE_NAME']};")
    db_max_collision_id = cursor.fetchone()[0]

    print(f"DB max collision ID: {db_max_collision_id}")
    print(f"API max collision ID: {api_max_collision_id}")
    print("")

    if db_max_collision_id is not None and db_max_collision_id >= api_max_collision_id:
        print("Staging table is up to date with OpenData API")
        print("exiting...")
        return

    lower_bound = db_max_collision_id+1 if db_max_collision_id is not None else 0
    upper_bound = (api_max_collision_id - api_max_collision_id % request_size) + request_size + 1

    print(f"found {api_max_collision_id} rows")
    print("Starting Requests")
    print("")

    select = 'crash_date,crash_time,borough,zip_code,latitude,longitude,on_street_name,cross_street_name,off_street_name,number_of_persons_injured,number_of_persons_killed,number_of_pedestrians_injured,number_of_pedestrians_killed,number_of_cyclist_injured,number_of_cyclist_killed,number_of_motorist_injured,number_of_motorist_killed,contributing_factor_vehicle_1,contributing_factor_vehicle_2,contributing_factor_vehicle_3,contributing_factor_vehicle_4,contributing_factor_vehicle_5,collision_id,vehicle_type_code1 as vehicle_type_code_1,vehicle_type_code2 as vehicle_type_code_2,vehicle_type_code_3,vehicle_type_code_4,vehicle_type_code_5'
    for bound in range(lower_bound, upper_bound, request_size):
        print(f'requesting id {bound} to {bound + request_size} from {api_max_collision_id}')
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

        cleanuped_results = cleanup_data(results)
        insert_to_staging(cursor, cleanuped_results, DB_CONFIG.TABLE_NAMES['STAGING_TABLE_NAME'])
        conn.commit()

        # print(f'\n{round(bound / upper_bound * 100)}% Done')
        progress_bar(lower_bound + total, api_max_collision_id)
        print('')

    print(f"sum: {total}")

if __name__ == "__main__":
    main()