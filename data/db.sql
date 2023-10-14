CREATE TABLE IF NOT EXISTS staging (
    crash_date DATE,
    crash_time TIME,
    borough TEXT,
    zip_code TEXT,
    latitude FLOAT,
    longitude FLOAT,
    on_street_name TEXT,
    cross_street_name TEXT,
    off_street_name TEXT,
    number_of_persons_injured INT,
    number_of_persons_killed INT,
    number_of_pedestrians_injured INT,
    number_of_pedestrians_killed INT,
    number_of_cyclist_injured INT,
    number_of_cyclist_killed INT,
    number_of_motorist_injured INT,
    number_of_motorist_killed INT,
    contributing_factor_vehicle_1 TEXT,
    contributing_factor_vehicle_2 TEXT,
    contributing_factor_vehicle_3 TEXT,
    contributing_factor_vehicle_4 TEXT,
    contributing_factor_vehicle_5 TEXT,
    collision_id INT PRIMARY KEY,
    vehicle_type_code_1 TEXT,
    vehicle_type_code_2 TEXT,
    vehicle_type_code_3 TEXT,
    vehicle_type_code_4 TEXT,
    vehicle_type_code_5 TEXT
);


CREATE TABLE IF NOT EXISTS dim_contributing_factors (
    contributing_factor_id SERIAL PRIMARY KEY,
    contributing_factor VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS dim_vehicles (
    vehicle_id SERIAL PRIMARY KEY,
    vehicle_type VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS dim_addresses (
    address_id SERIAL PRIMARY KEY,
    borough VARCHAR(255),
    zip_code VARCHAR(255),
    on_street_name VARCHAR(255),
    cross_street_name VARCHAR(255),
    off_street_name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS dim_timestamps (
    timestamp_id SERIAL PRIMARY KEY,
    hour INTEGER,
    day INTEGER,
    month INTEGER,
    year INTEGER,
    date_obj TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_coordinates (
    coordinates_id SERIAL PRIMARY KEY,
    latitude DECIMAL(9,6) NOT NULL, 
    longitude DECIMAL(9,6) NOT NULL
);

CREATE TABLE fact_accidents (
    accident_id SERIAL PRIMARY KEY,
    collision_id INTEGER,
    n_vehicles INTEGER,
    n_victims INTEGER,
    timestamp_id INTEGER,
    address_id INTEGER,
    coordinate_id INTEGER,
    vehicle1_id INTEGER,
    vehicle2_id INTEGER,
    vehicle3_id INTEGER,
    vehicle4_id INTEGER,
    vehicle5_id INTEGER,
    n_injured INTEGER,
    n_killed INTEGER,
    contributing_factor1_id INTEGER,
    contributing_factor2_id INTEGER,
    contributing_factor3_id INTEGER,
    contributing_factor4_id INTEGER,
    contributing_factor5_id INTEGER
);
