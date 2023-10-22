from utils.database import setup_db_connection

def truncate_table(cursor, table_name):
    query = f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;"
    try:
        cursor.execute(query)
        print(f"Successfully truncated the {table_name} table and reset its identity column.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():

    table_names = ["dim_addresses", "dim_coordinates", "dim_timestamps", "fact_accidents"]

    response = input(f"WARNING! Tables {table_names} are going to be truncated (yes/no): ")
    
    if response.lower() != "yes":
        print("exiting")
        return

    # Setup the database connection using the function from db_utils
    conn, cursor = setup_db_connection()

    for table_name in table_names:
        truncate_table(cursor, table_name)

    # Remember to close the connection after using it.
    cursor.close()
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()