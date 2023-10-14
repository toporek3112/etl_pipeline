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
    contributing_factor TEXT
);

CREATE TABLE IF NOT EXISTS dim_vehicles (
    vehicle_id SERIAL PRIMARY KEY,
    vehicle_type TEXT
);

-- CREATE TABLE IF NOT EXISTS dim_contributing_factors (
--     contributing_factor_id SERIAL PRIMARY KEY,
--     contributing_factor_original TEXT,
--     contributing_factor_corrected TEXT
-- );

-- CREATE TABLE IF NOT EXISTS dim_vehicles (
--     vehicle_id SERIAL PRIMARY KEY,
--     vehicle_type_original TEXT,
--     vehicle_type_corrected TEXT
-- );

-- commands
-- select count(staging.borough), staging.borough from staging group by borough order by count;
-- select count(staging.zip_code), staging.zip_code from staging group by zip_code order by count;
-- select count(staging.on_street_name), staging.on_street_name from staging group by staging.on_street_name order by count;
-- select count(staging.off_street_name), staging.off_street_name from staging group by staging.off_street_name order by count DESC, staging.off_street_name ASC;

-- SELECT 
--     COUNT(TRIM(staging.off_street_name)) AS count_off_street_name, 
--     TRIM(staging.off_street_name) AS trimmed_off_street_name 
-- FROM 
--     staging 
-- GROUP BY 
--     TRIM(staging.off_street_name) 
-- ORDER BY 
--     count_off_street_name DESC, 
--     trimmed_off_street_name ASC;

-- SELECT 
--     COUNT(staging.off_street_name) AS count_off_street_name, 
--     LOWER(staging.off_street_name) AS lowercase_off_street_name 
-- FROM 
--     staging 
-- GROUP BY 
--     LOWER(staging.off_street_name) 
-- ORDER BY 
--     count_off_street_name DESC, 
--     lowercase_off_street_name ASC;

  