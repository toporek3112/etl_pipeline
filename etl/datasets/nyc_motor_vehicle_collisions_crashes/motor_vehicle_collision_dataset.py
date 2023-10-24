import os
from etl.utils.dataset import Dataset
from etl.datasets.nyc_motor_vehicle_collisions_crashes.motor_vehicle_collision import create_collision
from etl.utils.socrata_api import SocrataClient  # Adjust the import path if necessary
from etl.utils.database import DatabaseConfig, DatabaseConnection
from etl.utils.loading_animation import ProgressBar
from etl.utils.phase_decorator import phase
import csv
import pandas as pd

class MotorVehicleCollisionDataset(Dataset):
    _instance = None
    current_directory = os.path.dirname(os.path.abspath(__file__))
    path_db_config = os.path.join(current_directory, 'database', 'db_config.json')
    path_db_create_tables = os.path.join(current_directory, 'database', 'create_tables.sql') 
    path_correction_file = os.path.join(current_directory, 'corrections')
    
    CHUNK_SIZE_LOAD = 20000
    CHUNK_SIZE_EXTRACT = 10000
    file_names = {
        "contributingFactors": "stagingContributingFactorsCorrected.csv",
        "vechicleTypes": "stagingVehicleTypesCorrected.csv"
      }

    def __init__(self, metadata: str = None):
        self.metadata = metadata
        self.socrata_client = SocrataClient(metadata['datasources'][0]['api_domain'], metadata['datasources'][0]['api_app_token'])
        self.db_config = DatabaseConfig(self.path_db_config, self.path_db_create_tables)
        self.db_connection = DatabaseConnection(self.db_config)
        self.cursor = self.db_connection.cursor
        self.max_socrata_id = 0
        self.max_database_id = 0
    
    ##############################################
    ################## EXTRACT ###################
    ##############################################

    def __get_max_id_from_socrata(self):
      max_collision_id = int(self.socrata_client.client.get(
          self.metadata['datasources'][0]['dataset_id'],
          select='max(collision_id)')[0]["max_collision_id"]
        )
      print(f"SOCRATA max collision ID: {max_collision_id}")
      return max_collision_id 

    def __get_api_column_name(self, internal_column_name: str):
      # Directly map the two specific column names, leave others unchanged
      if internal_column_name == 'vehicle_type_code_1':
          return 'vehicle_type_code1'
      elif internal_column_name == 'vehicle_type_code_2':
          return 'vehicle_type_code2'
      else:
          return internal_column_name

    @phase
    def extract(self):
        self.max_socrata_id = self.__get_max_id_from_socrata()
        self.max_database_id = self.db_connection.get_max_id_from_database("collision_id", self.db_connection.config.table_names['STAGING_TABLE_NAME'], False)

        if self.max_database_id is not None and self.max_database_id >= self.max_socrata_id:
            print("\033[32mStaging table is up to date\033[0m")
            print("")
            return
        
        print("")
        print("Starting Requests")
        print("")

        lower_bound = self.max_database_id + 1 if self.max_database_id is not None else 0
        upper_bound = (self.max_socrata_id - self.max_socrata_id % self.CHUNK_SIZE_LOAD) + self.CHUNK_SIZE_LOAD + 1
        columns = [
                    'crash_date',
                    'crash_time',
                    'borough',
                    'zip_code',
                    'latitude',
                    'longitude',
                    'on_street_name',
                    'cross_street_name',
                    'off_street_name',
                    'number_of_persons_injured',
                    'number_of_persons_killed',
                    'number_of_pedestrians_injured',
                    'number_of_pedestrians_killed',
                    'number_of_cyclist_injured',
                    'number_of_cyclist_killed',
                    'number_of_motorist_injured',
                    'number_of_motorist_killed',
                    'contributing_factor_vehicle_1',
                    'contributing_factor_vehicle_2',
                    'contributing_factor_vehicle_3',
                    'contributing_factor_vehicle_4',
                    'contributing_factor_vehicle_5',
                    'collision_id',
                    'vehicle_type_code_1',
                    'vehicle_type_code_2',
                    'vehicle_type_code_3',
                    'vehicle_type_code_4',
                    'vehicle_type_code_5',
                  ]
        api_column_names = [self.__get_api_column_name(col) for col in columns]
        placeholders = ', '.join(['%s'] * len(columns))
        progress_bar = ProgressBar(upper_bound, 0, self.CHUNK_SIZE_LOAD)
        total = 0

        for bound in range(lower_bound, upper_bound, self.CHUNK_SIZE_LOAD):
            progress_bar.update(bound)
            where = (
                f'collision_id >= {bound} and collision_id < {bound + self.CHUNK_SIZE_LOAD} and ('
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
            results = self.socrata_client.client.get(self.metadata['datasources'][0]['dataset_id'], limit=self.CHUNK_SIZE_LOAD, where=where, select=', '.join(api_column_names))
            total += len(results)

            collisions = [create_collision(result) for result in results]

            # print(f'found {len(results)} results')
            # print('Writing to Staging Database')
            
            data = [tuple(getattr(collision, col, None) for col in columns) for collision in collisions]
            query = f'INSERT INTO {self.db_connection.config.table_names["STAGING_TABLE_NAME"]} ({", ".join(columns)}) VALUES ({placeholders})'
            
            self.cursor.executemany(query, data)
            self.db_connection.connection.commit()

        progress_bar.set_prompt(finish_message=f'✅ Finished found {total} entries')
        progress_bar.finished = True

    ##############################################
    ################# TRANSFORM ##################
    ##############################################

    @staticmethod
    def __is_value_present(csv_data, value):
        return any(row['original'] == value for row in csv_data)

    def __get_unique_values(self, columns):
      print("Fetching list of unique values from staging table for columns:")

      for column in columns:
         print(f" {column}")

      query = f"""
          SELECT DISTINCT factor FROM (
              {" UNION ALL ".join(f"(SELECT {column} AS factor FROM {self.db_connection.config.table_names['STAGING_TABLE_NAME']})" for column in columns)}
          ) AS subquery
          ORDER BY factor
      """
      self.cursor.execute(query)
      dbRes=self.cursor.fetchall()

      if dbRes is None:
          print("No entires for contributing factors found")
          return None

      unique_values = [value[0] for value in dbRes if value[0]]
      return unique_values
    
    def __set_correction_file_path(self, filename):
       self.path_correction_file = os.path.join(self.current_directory, 'corrections', filename)

    def __save_unique_values(self, filename: str, columns):
      csv_data = []
      unique_values = self.__get_unique_values(columns)
      self.__set_correction_file_path(filename)
      try:
          # Check if file exists and read the existing data
          with open(self.path_correction_file, mode='r', newline='', encoding='utf-8') as file:
              reader = csv.DictReader(file)
              csv_data = list(reader)

          # Check and append new unique values if they are not already present
          new_entries = [{"original": value, "corrected": ""} for value in unique_values if not MotorVehicleCollisionDataset.__is_value_present(csv_data, value)]
          csv_data.extend(new_entries)

      except FileNotFoundError:
          # If the file doesn't exist, create new entries for all unique values
          csv_data = [{"original": value, "corrected": ""} for value in unique_values]

      csv_data.sort(key=lambda row: row['original'].lower())
      # Write the updated data back to the file

      print("Saving values to:")
      print(f" {self.path_correction_file}")
      print("")
      with open(self.path_correction_file, mode='w', newline='', encoding='utf-8') as file:
          fieldnames = ['original', 'corrected']
          writer = csv.DictWriter(file, fieldnames=fieldnames)
          writer.writeheader()
          writer.writerows(csv_data)

    @phase
    def transform(self):
        columns = []
        for i in range(1, 6):
            columns.append(f'contributing_factor_vehicle_{i}')
        self.__save_unique_values(self.file_names["contributingFactors"], columns)
        
        columns = []
        for i in range(1, 6):
            columns.append(f'vehicle_type_code_{i}')
        self.__save_unique_values(self.file_names["vechicleTypes"], columns)

        print("Open files and correct values manually")
        user_input = input("Do you want to proceed? (yes/no): ").lower().strip()

        if user_input in ('y', 'yes', ''):
            print("")
        else:
            print("Stopping...")

    ##############################################
    #################### LOAD ####################
    ##############################################

    def __get_staging_table_row_count(self):
      # Check if staging table has rows
      print("Fetching rows count from staging table")
      self.cursor.execute(f"SELECT COUNT(*) FROM {self.db_connection.config.table_names['STAGING_TABLE_NAME']}")
      total_rows = self.cursor.fetchone()[0]

      if total_rows is None:
          raise print("Staging table is empty!")
      
      return total_rows

    @staticmethod
    def __get_id(row, result_dict):
        value = row['corrected'] if not pd.isna(row['corrected']) else row['original']
        res = result_dict.get(value)
        return res

    def __insert_into_dimension(self, table_name, columns, data):
        self.cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;")
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
            self.cursor.execute(query)
            print(f"Successfully inserted {len(data)} rows into {table_name}")

            result = self.cursor.fetchall()
            result_dict = dict((v, k) for k, v in result)
            data['id'] = data.apply(lambda row: MotorVehicleCollisionDataset.__get_id(row, result_dict), axis=1)
            data['id'] = data['id']
            return data

        except Exception as e:
            print(f"An error occurred: {e}")

    def __insert_timestamp_data(self, data_chunk):
        timestamp_ids = []  # List to store the returned timestamp_ids

        # Prepare data for insertion
        values_str_list = []
        for i, row in data_chunk.iterrows():
            date_value, time_value = row['crash_date'], row['crash_time']  # assuming the date and time are the first two columns
            hour = time_value.hour
            day = date_value.day
            month = date_value.month
            year = date_value.year
            date_obj = f'{year}-{month:02d}-{day:02d} {hour:02d}:00:00'

            values_str = f"({hour}, {day}, {month}, {year}, '{date_obj}')"
            values_str_list.append(values_str)

        values_str = ', '.join(values_str_list)

        query = (
            f"INSERT INTO {self.db_connection.config.table_names['DIM_TIMESTAMPS_TABLE_NAME']} (hour, day, month, year, date_obj) "
            f"VALUES {values_str} "
            f"RETURNING timestamp_id;"
        )

        self.cursor.execute(query)
        result = self.cursor.fetchall()
        timestamp_ids = [row[0] for row in result]

        return timestamp_ids  # Return the list of timestamp_ids

    def __insert_coordinates_data(self, data_chunk):
        coordinates_data = [(row['latitude'], row['longitude']) for i, row in data_chunk.iterrows()]  # Prepare data for insertion

        # Build the VALUES clauses and the data list for the query
        values_clauses = ', '.join(['(%s, %s)'] * len(coordinates_data))
        data = [item for sublist in coordinates_data for item in sublist]  # Flatten the coordinates_data list

        query = f'INSERT INTO "{self.db_connection.config.table_names["DIM_COORDINATES_TABLE_NAME"]}" (latitude, longitude) VALUES {values_clauses} RETURNING coordinates_id;'

        self.cursor.execute(query, data)

        result = self.cursor.fetchall()
        coordinates_ids = [row[0] for row in result]

        return coordinates_ids

    def __insert_address_data(self, data_chunk):
        # Prepare data for insertion; assume that the relevant columns are at indices 2 to 7 in each row
        address_data = [(row['borough'], row['zip_code'], row['on_street_name'], row['cross_street_name'], row['off_street_name']) for i, row in data_chunk.iterrows()]

        # Build the VALUES clauses and the data list for the query
        values_clauses = ', '.join(['(%s, %s, %s, %s, %s)'] * len(address_data))
        data = [item for sublist in address_data for item in sublist]  # Flatten the address_data list

        query = f'''
            INSERT INTO "{self.db_connection.config.table_names['DIM_ADDRESSES_TABLE_NAME']}" (borough, zip_code, on_street_name, off_street_name, cross_street_name)
            VALUES {values_clauses}
            RETURNING address_id;
        '''

        self.cursor.execute(query, data)

        result = self.cursor.fetchall()
        address_ids = [row[0] for row in result]

        return address_ids

    def __insert_accident_data(self, data_chunk, contributing_factors, vehicle_types, timestamps_ids, addresses_ids, coordinates_ids):
        # Perform vectorized operations outside the loop
        n_vehicles = data_chunk.iloc[:, 23:28].notnull().sum(axis=1)
        n_injured = data_chunk.iloc[:, 9:16:2].fillna(0).sum(axis=1)
        n_killed = data_chunk.iloc[:, 10:17:2].fillna(0).sum(axis=1)
        n_victims = n_injured + n_killed

        accident_data = []
        for i, row in data_chunk.iterrows():
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

            row.fillna(0, inplace=True)
            # Use the previously computed series for n_vehicles, n_victims, n_injured, and n_killed
            accident_row = (
                row['collision_id'],  # collision_id
                int(n_vehicles.iat[i]),  # using iat for scalar lookups
                int(n_victims.iat[i]),
                timestamps_ids[i],
                addresses_ids[i],
                coordinates_ids[i],
                *corrected_vehicle_types,
                int(n_injured.iat[i]),
                int(n_killed.iat[i]),
                row['number_of_persons_injured'],
                row['number_of_persons_killed'],
                row['number_of_pedestrians_injured'],
                row['number_of_pedestrians_killed'],
                row['number_of_cyclist_injured'],
                row['number_of_cyclist_killed'],
                row['number_of_motorist_injured'],
                row['number_of_motorist_killed'],
                *corrected_contributing_factors
            )
            accident_data.append(accident_row)

        query = f'''
            INSERT INTO "{self.db_connection.config.table_names['FACT_ACCIDENTS_TABLE_NAME']}" (
                collision_id,
                n_vehicles,
                n_victims,
                timestamp_id,
                address_id,
                coordinate_id,
                vehicle1_id,
                vehicle2_id,
                vehicle3_id,
                vehicle4_id,
                vehicle5_id,
                n_injured,
                n_killed,
                n_persons_injured,
                n_persons_killed,
                n_pedestrians_injured,
                n_pedestrians_killed,
                n_cyclist_injured,
                n_cyclist_killed,
                n_motorist_injured,
                n_motorist_killed,
                contributing_factor1_id,
                contributing_factor2_id,
                contributing_factor3_id,
                contributing_factor4_id,
                contributing_factor5_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        '''

        self.cursor.executemany(query, accident_data)

    @phase
    def load(self):
        total_rows_count = self.__get_staging_table_row_count()

        print(f"Found {total_rows_count} rows in staging table")
        print("Starting preparing dimension tables...")
        print("")

        # Load corrected contributing factors from csv file from script 02_prepareForCorrection.py
        self.__set_correction_file_path(self.file_names["contributingFactors"])
        contributing_factors = pd.read_csv(self.path_correction_file)
        contributing_factors = self.__insert_into_dimension(
            self.db_connection.config.table_names['DIM_CONTRIBUTING_FACTORS_TABLE_NAME'],
            ["contributing_factor"],
            contributing_factors
          )

        # Load corrected vechicle types from csv file from script 02_prepareForCorrection.py
        self.__set_correction_file_path(self.file_names["vechicleTypes"])
        vehicle_types = pd.read_csv(self.path_correction_file)
        vehicle_types = self.__insert_into_dimension(
            self.db_connection.config.table_names['DIM_VEHICLES_TABLE_NAME'],
            ["vehicle_type"],
            vehicle_types
          )

        print("")

        # Select rows count to set lower bound
        self.cursor.execute(f'select count(*) from fact_accidents;')
        dbRes = self.cursor.fetchone()[0]
        lower_bound = dbRes+1 if dbRes is not None else 0

        print("")
        print("Starting loading data from staging table into dimension and fact tables...")
        
        progress_bar = ProgressBar(total_rows_count, 0, self.CHUNK_SIZE_EXTRACT)
        print("")
        # loading.set_prompt(finish_message='Finished!✅', failed_message='Failed!❌😨😨')

        for offset in range(lower_bound, total_rows_count, self.CHUNK_SIZE_EXTRACT):
            progress_bar.update(offset)

            self.cursor.execute(f"SELECT * FROM {self.db_connection.config.table_names['STAGING_TABLE_NAME']} LIMIT {self.CHUNK_SIZE_EXTRACT} OFFSET {offset}")
            data_chunk = self.cursor.fetchall()
            data_chunk_columns = [desc[0] for desc in self.cursor.description]
            data_chunk_df = pd.DataFrame(data_chunk, columns=data_chunk_columns)

            # insert timestamp
            timestamps_ids = self.__insert_timestamp_data(data_chunk_df)

            # Insert coordinates
            coordinates_ids = self.__insert_coordinates_data(data_chunk_df)

            # Insert addresses
            addresses_ids = self.__insert_address_data(data_chunk_df)

            self.__insert_accident_data(
                data_chunk_df,  
                contributing_factors, 
                vehicle_types, 
                timestamps_ids, 
                addresses_ids, 
                coordinates_ids)

            self.db_connection.connection.commit()  # Commit the transaction
        
        progress_bar.finished = True
        
