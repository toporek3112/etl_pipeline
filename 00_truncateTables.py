from utils.database import setup_db_connection

def truncate_table(cursor, table_name):
    query = f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;"
    try:
        cursor.execute(query)
        print(f"Successfully truncated the {table_name} table and reset its identity column.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    # Setup the database connection using the function from db_utils
    conn, cursor = setup_db_connection()

    truncate_table(cursor, "dim_addresses")
    truncate_table(cursor, "dim_coordinates")
    truncate_table(cursor, "dim_timestamps")
    truncate_table(cursor, "fact_accidents")

    # Remember to close the connection after using it.
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()