import csv
from utils.database import setup_db_connection, DB_CONFIG

def is_value_present(csv_data, value):
    return any(row['original'] == value for row in csv_data)

def get_unique_values(cursor, columns):
    print(f"Fetching list of unique values from database for columns: {', '.join(columns)}")

    query = f"""
        SELECT DISTINCT factor FROM (
            {" UNION ALL ".join(f"(SELECT {column} AS factor FROM {DB_CONFIG.TABLE_NAMES['STAGING_TABLE_NAME']})" for column in columns)}
        ) AS subquery
        ORDER BY factor
    """
    cursor.execute(query)
    dbRes=cursor.fetchall()
    
    if dbRes is None:
        print("No entires for contributing factors found")
        return None

    unique_values = [value[0] for value in dbRes if value[0]]
    return unique_values

def save_unique_values(unique_values, file_path):
    csv_data = []
    try:
        # Check if file exists and read the existing data
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            csv_data = list(reader)

        # Check and append new unique values if they are not already present
        new_entries = [{"original": value, "corrected": ""} for value in unique_values if not is_value_present(csv_data, value)]
        csv_data.extend(new_entries)

    except FileNotFoundError:
        # If the file doesn't exist, create new entries for all unique values
        csv_data = [{"original": value, "corrected": ""} for value in unique_values]

    csv_data.sort(key=lambda row: row['original'].lower())
    # Write the updated data back to the file
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ['original', 'corrected']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)

def main():
    conn, cursor = setup_db_connection()

    print("Fetching list of unique contributing_factors from database")
    columns = []

    for i in range(1, 6):
        columns.append(f'contributing_factor_vehicle_{i}')

    unique_cf = get_unique_values(cursor, columns)
    save_unique_values(unique_cf, 'data/stagingContributingFactorsCorrected.csv')

    print("Fetching list of unique vehicle types from database")

    for i in range(1, 6):
        columns.append(f'vehicle_type_code_{i}')

    unique_vt = get_unique_values(cursor, columns)
    save_unique_values(unique_vt, 'data/stagingVehicleTypesCorrected.csv')

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()