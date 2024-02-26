from ams_dataset import ams_dataset
from etl.utils.database import DatabaseConfig, DatabaseConnection
import os

class ArbeitslosigkeitBestandDataset(ams_dataset):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    db_config_path = os.path.join(current_directory, 'database', 'db_config.json')
    db_create_tables_path = os.path.join(current_directory, 'database', 'create_tables.sql')
    
    def __init__(self, metadata: str,):
        self.metadata = metadata
        self.db_config = DatabaseConfig(self.db_config_path, self.db_create_tables_path)
        self.db_connection = DatabaseConnection(self.db_config)

    def get_csv(self):
        # Define the logic for fetching data from the Socrata API
        # Assume the fetch logic returns a list of dictionaries where each dictionary represents a motor vehicle collision
        print("Get csv and save it")

    def extract_and_save(self):
        # Define the logic for fetching data from the Socrata API
        # Assume the fetch logic returns a list of dictionaries where each dictionary represents a motor vehicle collision
        print("Do something with csv")

