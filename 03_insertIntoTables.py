import pandas as pd
import sys
from utils.time_decorator import timer
from utils.database import setup_db_connection, DB_CONFIG

def progress_bar(cur_index:int,total:int):
    percent = round((cur_index+1) / total * 100)
    prog = round(percent/5)
    sys.stdout.write('\r')
    sys.stdout.write('['+'='*prog+'.'*(20-prog)+f'] {percent}%')
    sys.stdout.flush()

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

def get_id(row, result_dict):
    value = row['corrected'] if not pd.isna(row['corrected']) else row['original']
    res = result_dict.get(value)
    return res

def insert_into_dimension(cursor, table_name, columns, data):
    truncate_table(cursor, table_name)
    print(f"Inserting into dimension table {table_name}")

    # Build the values string for the query
    values_str_list = []
    for i, row in data.iterrows():
        if pd.isnull(row['corrected']):
            values_str_list.append(f"('{row['original']}')")
        else:
            values_str_list.append(f"('{row['corrected']}')")
    
    # Convert the list to a Series
    values_series = pd.Series(values_str_list)
    unique_values_series = values_series.drop_duplicates()

    # Join the values into a single string for the query
    values_str = ','.join(unique_values_series)
    
    query = (
        f"INSERT INTO {table_name} ({', '.join(columns)}) "
        f"VALUES {values_str} "
        f"RETURNING *"
    )

    try:
    # Execute the query with the data
        cursor.execute(query)
        print(f"Successfully inserted {len(data)} rows into {table_name}")

        result = cursor.fetchall()
        result_dict = dict((v, k) for k, v in result)
        data['id'] = data.apply(lambda row: get_id(row, result_dict), axis=1)
        data['id'] = data['id']
        return data

    except Exception as e:
        print(f"An error occurred: {e}")

def generate_insert_string_with_returning(table: str, contents: dict, returning_column: str) -> str:
    sql_keys = ', '.join(f'"{k}"' for k in contents.keys())
    escaped_values = [str(v).replace("'", "''") for v in contents.values()]
    sql_values = ', '.join(f"'{v}'" for v in escaped_values)
    
    query = (
        f'INSERT INTO "{table}" ({sql_keys})\n'
        f'VALUES ({sql_values})\n'
        f'RETURNING "{returning_column}"'
    )
    
    return query

def insert_timestamp_data(cursor, data_chunk, table_name):
    timestamp_ids = []  # List to store the returned timestamp_ids

    # Prepare data for insertion
    values_str_list = []
    for row in data_chunk:
        date_value, time_value = row[0], row[1]  # assuming the date and time are the first two columns
        hour = time_value.hour
        day = date_value.day
        month = date_value.month
        year = date_value.year
        date_obj = f'{year}-{month:02d}-{day:02d} {hour:02d}:00:00'

        values_str = f"({hour}, {day}, {month}, {year}, '{date_obj}')"
        values_str_list.append(values_str)
    
    values_str = ', '.join(values_str_list)
    
    query = (
        f"INSERT INTO {table_name} (hour, day, month, year, date_obj) "
        f"VALUES {values_str} "
        f"RETURNING timestamp_id;"
    )

    cursor.execute(query)
    result = cursor.fetchall()
    timestamp_ids = [row[0] for row in result]

    return timestamp_ids  # Return the list of timestamp_ids

def insert_coordinates_data(cursor, data_chunk, table_name):
    coordinates_data = [(row[4], row[5]) for row in data_chunk]  # Prepare data for insertion
    
    # Build the VALUES clauses and the data list for the query
    values_clauses = ', '.join(['(%s, %s)'] * len(coordinates_data))
    data = [item for sublist in coordinates_data for item in sublist]  # Flatten the coordinates_data list
    
    query = f'INSERT INTO "{table_name}" (latitude, longitude) VALUES {values_clauses} RETURNING coordinates_id;'
    
    cursor.execute(query, data)
    
    result = cursor.fetchall()
    coordinates_ids = [row[0] for row in result]

    return coordinates_ids

def insert_address_data(cursor, data_chunk, table_name):
    # Prepare data for insertion; assume that the relevant columns are at indices 2 to 7 in each row
    address_data = [(row[2], row[3], row[6], row[7], row[8]) for row in data_chunk]
    
    # Build the VALUES clauses and the data list for the query
    values_clauses = ', '.join(['(%s, %s, %s, %s, %s)'] * len(address_data))
    data = [item for sublist in address_data for item in sublist]  # Flatten the address_data list

    query = f'''
        INSERT INTO "{table_name}" (borough, zip_code, on_street_name, off_street_name, cross_street_name)
        VALUES {values_clauses}
        RETURNING address_id;
    '''
    
    cursor.execute(query, data)
    
    result = cursor.fetchall()
    address_ids = [row[0] for row in result]

    return address_ids

def insert_accident_data(cursor, data_chunk, table_name, contributing_factors, vehicle_types, timestamps_ids, addresses_ids, coordinates_ids):
    accident_data = []
    for i, row in enumerate(data_chunk):
        n_vehicles = sum(1 for vehicle_type in row[23:28] if vehicle_type is not None)  # Assuming vehicle ids are in columns 25-29
        n_victims = n_victims = sum((0 if value is None else value) for value in (row[j] for j in range(9, 17)))  # Summing values from number_of_persons_injured to number_of_motorist_killed
        
        if n_victims != 0:
            n_injured = n_injured = sum((0 if value is None else value) for value in (row[j] for j in range(9, 16, 2)))  # Summing the injured counts from each category
            n_killed = n_killed = sum((0 if value is None else value) for value in (row[j] for j in range(10, 17, 2)))  # Summing the killed counts from each category
        else:
            n_injured = 0
            n_killed = 0

        # Correct contributing factors using the dictionary
        corrected_contributing_factors = []
        for factor in row[17:22]:
            if factor is not None:
                filtered_df = contributing_factors[contributing_factors['original'] == factor]
                ct_id = None if filtered_df.empty else int(filtered_df['id'].values[0])
                corrected_contributing_factors.append(ct_id)
            else:
                corrected_contributing_factors.append(None)

        corrected_vehicle_types = []
        for vehicle_type in row[23:28]:
            if vehicle_type is not None:
                filtered_df = vehicle_types[vehicle_types['original'] == vehicle_type]
                vt_id = None if filtered_df.empty else int(filtered_df['id'].values[0])
                corrected_vehicle_types.append(vt_id)
            else:
                corrected_vehicle_types.append(None)

        
        accident_row = (
            row[22],  # collision_id
            n_vehicles,
            n_victims,
            timestamps_ids[i],
            addresses_ids[i],
            coordinates_ids[i],
            *corrected_vehicle_types,
            n_injured,
            n_killed,
            *corrected_contributing_factors
        )
        accident_data.append(accident_row)

    query = f'''
        INSERT INTO "{table_name}" (
            collision_id, n_vehicles, n_victims, timestamp_id, address_id, coordinate_id,
            vehicle1_id, vehicle2_id, vehicle3_id, vehicle4_id, vehicle5_id,
            n_injured, n_killed,
            contributing_factor1_id, contributing_factor2_id, contributing_factor3_id, contributing_factor4_id, contributing_factor5_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    '''

    cursor.executemany(query, accident_data)

@timer
def main():
    conn, cursor = setup_db_connection()
    print("")

    # Check if staging table has rows
    print("Fetching rows count from staging table")
    cursor.execute(f"SELECT COUNT(*) FROM {DB_CONFIG.TABLE_NAMES['STAGING_TABLE_NAME']}")
    total_rows = cursor.fetchone()[0]
    chunk_size = 1000

    if total_rows is None:
        print("Staging table is empty!")
        return
    
    print(f"Found {total_rows} rows in staging table")
    print("Starting preparing dimension tables...")
    print("")
    
    print("")

    # Load corrected contributing factors
    contributing_factors = pd.read_csv("data/stagingContributingFactorsCorrected.csv")
    columns = ["contributing_factor"]
    contributing_factors = insert_into_dimension(cursor, "dim_contributing_factors", columns, contributing_factors)

    print("")

    # Load corrected vechicle types
    vehicle_types = pd.read_csv("data/stagingVehicleTypesCorrected.csv")
    columns = ["vehicle_type"]
    vehicle_types = insert_into_dimension(cursor, "dim_vehicles", columns, vehicle_types)
    
    cursor.execute(f'select count(*) from fact_accidents;')
    dbRes = cursor.fetchone()[0]
    lower_bound = dbRes+1 if dbRes is not None else 0

    print("")
    print("Starting loading data from staging table...")
    for offset in range(lower_bound, total_rows, chunk_size):
        
        print(f"Querying entries {offset} to {offset + chunk_size} from {total_rows}")
        progress_bar(offset, total_rows)
        print("")

        cursor.execute(f"SELECT * FROM {DB_CONFIG.TABLE_NAMES['STAGING_TABLE_NAME']} LIMIT {chunk_size} OFFSET {offset}")
        data_chunk = cursor.fetchall()
        
        # insert timestamp
        table_name = "dim_timestamps"
        timestamps_ids = insert_timestamp_data(cursor, data_chunk, table_name)

        # Insert coordinates
        table_name_coordinates = "dim_coordinates"
        coordinates_ids = insert_coordinates_data(cursor, data_chunk, table_name_coordinates)

        # Insert addresses
        table_name_addresses = "dim_addresses"
        addresses_ids = insert_address_data(cursor, data_chunk, table_name_addresses)

        table_name_accidents = "fact_accidents"
        insert_accident_data(
            cursor,
            data_chunk, 
            table_name_accidents, 
            contributing_factors, 
            vehicle_types, 
            timestamps_ids, 
            addresses_ids, 
            coordinates_ids)
        
        conn.commit()  # Commit the transaction


    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
