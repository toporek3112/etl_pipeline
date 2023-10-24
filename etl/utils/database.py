import json
import re
import psycopg2

class DatabaseConfig:
    print("DB: loding database config")
    def __init__(self, config_path, create_tables_path):
        self.config_path = config_path
        self.create_tables_path = create_tables_path
        self.database_settings = None
        self.table_names = {}
        self.load_config()

    def extract_table_names_from_sql(self):
        with open(self.create_tables_path, 'r') as file:
            sql_content = file.read()

        pattern = re.compile(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([\w_]+)', re.IGNORECASE)
        return pattern.findall(sql_content)

    def load_config(self):
        with open(self.config_path, 'r') as file:
            config = json.load(file)

        self.database_settings = config['database_settings']
        table_names = self.extract_table_names_from_sql()
        self.table_names = {name.upper() + '_TABLE_NAME': name for name in table_names}

class DatabaseConnection:
    _instance = None

    def __new__(cls, db_config):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.db_config = db_config
            cls._instance.initialized = False
        return cls._instance

    def __init__(self, db_config):
        if not self._instance.initialized:
            
            print("DB: connecting to postgres")
            conn = psycopg2.connect(user=db_config.database_settings['user'],
                                    password=db_config.database_settings['password'],
                                    host=db_config.database_settings['host'],
                                    port=db_config.database_settings['port'],
                                    database='postgres')  # or another default database
            conn.autocommit = True  # Enable autocommit mode to execute the CREATE DATABASE command
            cursor = conn.cursor()

            print(f"DB: checking if database {db_config.database_settings['database']} exists")
            cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{db_config.database_settings['database']}';")
            db_exists = cursor.fetchone()

            # Step 3: Create Database (if necessary)
            if not db_exists:
                print("DB: database not present, creating...")
                cursor.execute(f"CREATE DATABASE {db_config.database_settings['database']};")

            # Close the initial connection
            cursor.close()
            conn.close()

            # Step 4: Connect to the New Database
            self._instance._connection = psycopg2.connect(**db_config.database_settings)
            self._instance._connection.autocommit = False
            self._instance._cursor = self._instance._connection.cursor()

            # Steps 5 and 6: Check Table Existence and Create Tables (if necessary)
            # Load the table creation queries from file
            print("DB: checking tables")
            with open(db_config.create_tables_path, 'r') as file:  # This line uses the provided path
                create_tables_query = file.read()

            # Execute the table creation queries
            self._instance._cursor.execute(create_tables_query)
            self._instance._connection.commit()

            print("DB: database ready to go!")
            print("")
            self._instance.initialized = True

    @property
    def cursor(self):
        return self._instance._cursor

    @property
    def connection(self):
        return self._instance._connection

    @property
    def config(self):
        return self._instance.db_config

    def get_max_id_from_database(self, id_field_name: int, table: str, quite: bool = True) -> int:
        self.cursor.execute(f"SELECT MAX({id_field_name}) FROM {table};")
        max_id = self.cursor.fetchone()[0]
        if not quite: print(f"DB max collision ID: {max_id}")
        return max_id