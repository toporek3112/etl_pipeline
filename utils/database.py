import json
import re
import os
import psycopg2


class DB_CONFIG:
    _loaded = False
    DATABASE_SETTINGS = None
    TABLE_NAMES = {}

    current_directory = os.path.dirname(os.path.abspath(__file__)) 
    db_config_path = os.path.join(current_directory, '..', 'data', 'database', 'db_config.json')
    db_create_tables_path = os.path.join(current_directory, '..', 'data', 'database', 'create_tables.sql')

    @classmethod
    def extract_table_names_from_sql(cls, file_path):
        with open(file_path, 'r') as f:
            sql_content = f.read()
        
        pattern = re.compile(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([\w_]+)', re.IGNORECASE)
        return pattern.findall(sql_content)

    @classmethod
    def load(cls):
        if not cls._loaded:
            with open(cls.db_config_path, 'r') as file:
                config = json.load(file)
            cls.DATABASE_SETTINGS = config['database_settings']
            
            # Load table names from SQL file
            table_names = cls.extract_table_names_from_sql(cls.db_create_tables_path)
            cls.TABLE_NAMES = {name.upper() + '_TABLE_NAME': name for name in table_names}
            
            cls._loaded = True

DB_CONFIG.load()  # This loads the config when the module is imported

def setup_db_connection():
    print("Setup Database Connection")

    conn = psycopg2.connect(**DB_CONFIG.DATABASE_SETTINGS)
    conn.autocommit = False
    cursor = conn.cursor()
    return conn, cursor