from etl.utils.time_decorator import timer
from etl.datasets.nyc_motor_vehicle_collisions_crashes.motor_vehicle_collision_dataset import MotorVehicleCollisionDataset
from etl.datasets.AMS.ams_dataset import AMSDataset

@timer
def transform(dataset_name: str):

    print("")   
    print("Phase: TRANSFORM")
    print("")

    # Handle datasets
    if dataset_name == "nyc_motor_vehicle_collisions_crashes":
        dataset = MotorVehicleCollisionDataset()
        dataset.save_contributing_factors()
        dataset.save_vehicle_types()
        print("")
        return
    elif dataset_name == "AMS":
        dataset = AMSDataset()
        dataset.get_csv()
    else:
        raise ValueError(f'Unknown dataset: {dataset_name}')

