import sys
from etl.utils.time_decorator import timer
from etl.datasets.nyc_motor_vehicle_collisions_crashes.motor_vehicle_collision_dataset import MotorVehicleCollisionDataset
from etl.datasets.AMS.ams_dataset import AMSDataset

def progress_bar(cur_index:int,total:int):
    percent = round((cur_index+1) / total * 100)
    prog = round(percent/5)
    sys.stdout.write('\r')
    sys.stdout.write('['+'='*prog+'.'*(20-prog)+f'] {percent}%')
    sys.stdout.flush()

@timer
def load(dataset_name: str):

    print("")   
    print("Phase: LOAD")
    print("")

    # Handle datasets
    if dataset_name == "nyc_motor_vehicle_collisions_crashes":
        dataset = MotorVehicleCollisionDataset()
        dataset.load()
        return
    elif dataset_name == "AMS":
        dataset = AMSDataset()
        dataset.get_csv()
    else:
        raise ValueError(f'Unknown dataset: {dataset_name}')
