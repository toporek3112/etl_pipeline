import os
from etl.extract import extract
from etl.transform import transform 
from etl.load import load 

def list_datasets():
    datasets_dir = os.path.join(os.getcwd(), 'etl/datasets')
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

def main():
    try:
        datasets = list_datasets()
        selected_dataset = select_dataset(datasets)
        print(f"Selected dataset: {selected_dataset}")

        extract(selected_dataset) 
        transform(selected_dataset)
        load(selected_dataset)  
    except KeyboardInterrupt:
        print("")
        print("Aborting...")
        exit()

if __name__ == "__main__":
    main()