import os
import json
import argparse
from prettytable import PrettyTable
from pipeline.datasets.nyc_motor_vehicle_collisions_crashes.motor_vehicle_collision import MotorVehicleCollision
from pipeline.datasets.nyc_motor_vehicle_collisions_crashes.motor_vehicle_collision_dataset import MotorVehicleCollisionDataset
from pipeline.datasets.AMS.ams_dataset import AMSDataset

def list_datasets():
    datasets_dir = os.path.join(os.getcwd(), 'pipeline/datasets')
    datasets = [d for d in os.listdir(datasets_dir) if os.path.isdir(os.path.join(datasets_dir, d))]
    return datasets

def select_dataset(datasets):
    while True:  # Keep prompting until a valid selection is made
        print("Available datasets:")
        for i, dataset in enumerate(datasets, start=1):
            print(f"{i}. {dataset}")

        print("")
        try:
            selection = int(input("Enter the number of the dataset you want to process: ")) - 1
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue  # Skip the rest of the loop and prompt again

        if 0 <= selection < len(datasets):
            return datasets[selection]  # Return the selected dataset if the selection is valid
        else:
            print(f"\033[31mInvalid selection. Please enter a number between 1 and {len(datasets)}.\033[0m")

def read_dataset_metadata(dataset: str):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    metadata_path = os.path.join(current_directory, "pipeline", 'datasets', dataset, 'metadata.json')
    with open(metadata_path, 'r', encoding='utf-8') as file:
        metadata = json.load(file)
    return metadata

def print_dataset_metadata(metadata: dict):
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

def main():
    try:
        parser = argparse.ArgumentParser(description='Your script description')
        parser.add_argument('--y', action='store_true', help='procced after transform phase')
        args = parser.parse_args()

        datasets = list_datasets()
        selected_dataset = select_dataset(datasets)
        print(f"Selected dataset: {selected_dataset}")
        
        # Handle datasets
        metadata = read_dataset_metadata(selected_dataset)
        print_dataset_metadata(metadata)
        if selected_dataset == "nyc_motor_vehicle_collisions_crashes":
            dataset = MotorVehicleCollisionDataset(metadata)
            dataset.extract()
            dataset.transform(args)
            dataset.load()
            return
        elif selected_dataset == "AMS":
            print("AMS dataset")
            # dataset = AMSDataset()
            # dataset.get_csv()
        else:
            raise ValueError(f'Unknown dataset: {selected_dataset}')

    except KeyboardInterrupt:
        print("")
        print("Aborting...")
        exit()

if __name__ == "__main__":
    main()