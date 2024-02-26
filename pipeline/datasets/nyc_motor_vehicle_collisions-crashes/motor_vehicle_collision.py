from typing import Optional

class MotorVehicleCollision:
  def __init__(
      self,
      crash_date: str,
      crash_time: str,
      borough: str,
      zip_code: str,
      latitude: float,
      longitude: float,
      on_street_name: str,
      off_street_name: str,
      cross_street_name: str,
      number_of_persons_injured: int,
      number_of_persons_killed: int,
      number_of_pedestrians_injured: int,
      number_of_pedestrians_killed: int,
      number_of_cyclist_injured: int,
      number_of_cyclist_killed: int,
      number_of_motorist_injured: int,
      number_of_motorist_killed: int,
      contributing_factor_vehicle_1: str,
      contributing_factor_vehicle_2: str,
      contributing_factor_vehicle_3: str,
      contributing_factor_vehicle_4: str,
      contributing_factor_vehicle_5: str,
      collision_id: int,
      vehicle_type_code1: str,
      vehicle_type_code2: str,
      vehicle_type_code_3: str,
      vehicle_type_code_4: str,
      vehicle_type_code_5: str
    ):
    self.crash_date = crash_date
    self.crash_time = crash_time
    self.borough = borough
    self.zip_code = zip_code
    self.latitude = latitude
    self.longitude = longitude
    self.on_street_name = on_street_name
    self.off_street_name = off_street_name
    self.cross_street_name = cross_street_name
    self.number_of_persons_injured = number_of_persons_injured
    self.number_of_persons_killed = number_of_persons_killed
    self.number_of_pedestrians_injured = number_of_pedestrians_injured
    self.number_of_pedestrians_killed = number_of_pedestrians_killed
    self.number_of_cyclist_injured = number_of_cyclist_injured
    self.number_of_cyclist_killed = number_of_cyclist_killed
    self.number_of_motorist_injured = number_of_motorist_injured
    self.number_of_motorist_killed = number_of_motorist_killed
    self.contributing_factor_vehicle_1 = contributing_factor_vehicle_1
    self.contributing_factor_vehicle_2 = contributing_factor_vehicle_2
    self.contributing_factor_vehicle_3 = contributing_factor_vehicle_3
    self.contributing_factor_vehicle_4 = contributing_factor_vehicle_4
    self.contributing_factor_vehicle_5 = contributing_factor_vehicle_5
    self.collision_id = collision_id
    self.vehicle_type_code1 = vehicle_type_code1
    self.vehicle_type_code2 = vehicle_type_code2
    self.vehicle_type_code_3 = vehicle_type_code_3
    self.vehicle_type_code_4 = vehicle_type_code_4
    self.vehicle_type_code_5 = vehicle_type_code_5

  def __repr__(self) -> str:
    return (f"MotorVehicleCollision("
            f"crash_date={self.crash_date!r}, "
            f"crash_time={self.crash_time!r}, "
            f"borough={self.borough!r}, "
            f"zip_code={self.zip_code!r}, "
            f"latitude={self.latitude!r}, "
            f"longitude={self.longitude!r}, "
            f"on_street_name={self.on_street_name!r}, "
            f"off_street_name={self.off_street_name!r}, "
            f"cross_street_name={self.cross_street_name!r}, "
            f"number_of_persons_injured={self.number_of_persons_injured!r}, "
            f"number_of_persons_killed={self.number_of_persons_killed!r}, "
            f"number_of_pedestrians_injured={self.number_of_pedestrians_injured!r}, "
            f"number_of_pedestrians_killed={self.number_of_pedestrians_killed!r}, "
            f"number_of_cyclist_injured={self.number_of_cyclist_injured!r}, "
            f"number_of_cyclist_killed={self.number_of_cyclist_killed!r}, "
            f"number_of_motorist_injured={self.number_of_motorist_injured!r}, "
            f"number_of_motorist_killed={self.number_of_motorist_killed!r}, "
            f"contributing_factor_vehicle_1={self.contributing_factor_vehicle_1!r}, "
            f"contributing_factor_vehicle_2={self.contributing_factor_vehicle_2!r}, "
            f"contributing_factor_vehicle_3={self.contributing_factor_vehicle_3!r}, "
            f"contributing_factor_vehicle_4={self.contributing_factor_vehicle_4!r}, "
            f"contributing_factor_vehicle_5={self.contributing_factor_vehicle_5!r}, "
            f"collision_id={self.collision_id!r}, "
            f"vehicle_type_code1={self.vehicle_type_code1!r}, "
            f"vehicle_type_code2={self.vehicle_type_code2!r}, "
            f"vehicle_type_code_3={self.vehicle_type_code_3!r}, "
            f"vehicle_type_code_4={self.vehicle_type_code_4!r}, "
            f"vehicle_type_code_5={self.vehicle_type_code_5!r})")

def validate_str(value: Optional[str], default: str = '') -> str:
    return (value.strip() if value is not None else default)

def validate_int(value: Optional[str], default: int = 0) -> int:
    try:
        return int(value) if value is not None else default
    except ValueError:
        return default

def validate_float(value: Optional[str], default: float = 0.0) -> float:
    try:
        return float(value) if value is not None else default
    except ValueError:
        return default

def create_collision(data: dict) -> MotorVehicleCollision:
    return MotorVehicleCollision(
        crash_date=validate_str(data.get('crash_date')),
        crash_time=validate_str(data.get('crash_time')),
        borough=validate_str(data.get('borough')),
        zip_code=validate_int(data.get('zip_code'), -1),
        latitude=validate_float(data.get('latitude')),
        longitude=validate_float(data.get('longitude')),
        on_street_name=validate_str(data.get('on_street_name')),
        off_street_name=validate_str(data.get('off_street_name')),
        cross_street_name=validate_str(data.get('cross_street_name')),
        number_of_persons_injured=validate_int(data.get('number_of_persons_injured')),
        number_of_persons_killed=validate_int(data.get('number_of_persons_killed')),
        number_of_pedestrians_injured=validate_int(data.get('number_of_pedestrians_injured')),
        number_of_pedestrians_killed=validate_int(data.get('number_of_pedestrians_killed')),
        number_of_cyclist_injured=validate_int(data.get('number_of_cyclist_injured')),
        number_of_cyclist_killed=validate_int(data.get('number_of_cyclist_killed')),
        number_of_motorist_injured=validate_int(data.get('number_of_motorist_injured')),
        number_of_motorist_killed=validate_int(data.get('number_of_motorist_killed')),
        contributing_factor_vehicle_1=validate_str(data.get('contributing_factor_vehicle_1')),
        contributing_factor_vehicle_2=validate_str(data.get('contributing_factor_vehicle_2')),
        contributing_factor_vehicle_3=validate_str(data.get('contributing_factor_vehicle_3')),
        contributing_factor_vehicle_4=validate_str(data.get('contributing_factor_vehicle_4')),
        contributing_factor_vehicle_5=validate_str(data.get('contributing_factor_vehicle_5')),
        collision_id=validate_int(data.get('collision_id')),
        vehicle_type_code1=validate_str(data.get('vehicle_type_code_1')),
        vehicle_type_code2=validate_str(data.get('vehicle_type_code_2')),
        vehicle_type_code_3=validate_str(data.get('vehicle_type_code_3')),
        vehicle_type_code_4=validate_str(data.get('vehicle_type_code_4')),
        vehicle_type_code_5=validate_str(data.get('vehicle_type_code_5'))
    )
