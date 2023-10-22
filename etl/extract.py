import sys
import os
import json
from typing import List
from prettytable import PrettyTable
from psycopg2.extensions import cursor as DBcursor
from etl.utils.time_decorator import timer
from etl.datasets.nyc_motor_vehicle_collisions_crashes.motor_vehicle_collision import MotorVehicleCollision
from etl.datasets.nyc_motor_vehicle_collisions_crashes.motor_vehicle_collision_dataset import MotorVehicleCollisionDataset
from etl.datasets.AMS.ams_dataset import AMSDataset

def read_dataset_metadata(dataset: str):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    metadata_path = os.path.join(current_directory, 'datasets', dataset, 'metadata.json')
    with open(metadata_path, 'r', encoding='utf-8') as file:
        metadata = json.load(file)
    return metadata

@timer
def extract(dataset_name: str):

    metadata = read_dataset_metadata(dataset_name)
    datasets_count = len(metadata['datasources'])
    if datasets_count > 1:
        print(f"There are {datasets_count} datasources in total")
    else:
        print("")
        table = PrettyTable()
        table.field_names = ["Property", "Value"]
        table.align["Property"] = "l"
        table.align["Value"] = "l"
        table.add_row(["Title", metadata['datasources'][0]['title']])
        table.add_row(["Website", metadata['datasources'][0]['website']])
        table.add_row(["Type", metadata['datasources'][0]['type']])
        table.add_row(["Source", metadata['datasources'][0]['source']])
        print(table)

    print("")   
    print("Phase: EXTRACT")
    print("")

    # Handle datasets
    if dataset_name == "nyc_motor_vehicle_collisions_crashes":
        dataset = MotorVehicleCollisionDataset(metadata)

        if dataset.max_database_id is not None and dataset.max_database_id >= dataset.max_socrata_id:
            print("\033[32mStaging table is up to date\033[0m")
            return

        dataset.extract_and_save()
        print()
        return
    elif dataset_name == "AMS":
        dataset = AMSDataset()
        dataset.get_csv()
    else:
        raise ValueError(f'Unknown dataset: {dataset_name}')
    
