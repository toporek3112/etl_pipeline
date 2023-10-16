# run postgres in docker
docker run --name postgres -p 5432:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=postgres -d postgres:latest
# run pgAdmin 
docker run --name pgadmin -p 5050:80  -e 'PGADMIN_DEFAULT_EMAIL=admin@admin.com' -e 'PGADMIN_DEFAULT_PASSWORD=postgres' -d dpage/pgadmin4
# http://localhost:5050

# get postgres ip
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' postgres

# connect to postgres
docker run --rm --link postgres:postgres -it postgres psql -h postgres -U postgres -d nyc_motor_vechicle_collisions
pgcli -h localhost -U postgres -d nyc_motor_vechicle_collisions

# create db database 
docker run --rm --link postgres:postgres -v $(pwd)/data/database:/tmp -it postgres psql -h postgres -U postgres -a -f /tmp/create_db.sql
# create db tables 
docker run --rm --link postgres:postgres -v $(pwd)/data/database:/tmp -it postgres psql -h postgres -U postgres -d nyc_motor_vechicle_collisions -a -f /tmp/create_tables.sql

# run Grafana
docker run -d --name=grafana -p 3000:3000 -e GF_SECURITY_ADMIN_USER=postgres -e GF_SECURITY_ADMIN_PASSWORD=postgres grafana/grafana
# http://localhost:3000
# export datasource
curl -u postgres:postgres http://localhost:3000/api/datasources

###### docker compose ######
docker-compose -f docker-compose.yaml -f docker-compose.overwrite.yaml up -d # with persistence 
docker-compose up -d # no persistence


# Database commands
SELECT contributing_factor_vehicle_1, contributing_factor_vehicle_2, contributing_factor_vehicle_3, contributing_factor_vehicle_4, contributing_factor_vehicle_5 FROM staging;
SELECT contributing_factor_vehicle_1 FROM staging where contributing_factor_vehicle_1 == NULL;

(SELECT contributing_factor_vehicle_1 FROM staging)
UNION
(SELECT contributing_factor_vehicle_2 FROM staging)
UNION
(SELECT contributing_factor_vehicle_3 FROM staging)
UNION
(SELECT contributing_factor_vehicle_4 FROM staging)
UNION
(SELECT contributing_factor_vehicle_5 FROM staging)
ORDER BY 1

(SELECT vehicle_type_code_1 FROM staging)
UNION
(SELECT vehicle_type_code_2 FROM staging)
UNION
(SELECT vehicle_type_code_3 FROM staging)
UNION
(SELECT vehicle_type_code_4 FROM staging)
UNION
(SELECT vehicle_type_code_5 FROM staging)
ORDER BY 1

SELECT *
FROM fact_accidents fa
JOIN dim_timestamps dt ON fa.timestamp_id = dt.timestamp_id;

SELECT 
  n_vehicles AS "Vehivles Involved", 
  n_victims AS "Victims",
  n_injured AS "Injured",
  n_killed AS "Killed",
  fa.timestamp_id,
  dt.timestamp_id AS "timestamp_id_dt",
  hour,
  day,
  month,
  year
FROM fact_accidents fa
JOIN dim_timestamps dt ON fa.timestamp_id = dt.timestamp_id 
LIMIT 50 

SELECT 
  SUM(n_killed) AS "Killed",
  fa.timestamp_id,
  dt.timestamp_id AS "timestamp_id_dt",
  year
FROM fact_accidents fa
JOIN dim_timestamps dt ON fa.timestamp_id = dt.timestamp_id
GROUP BY year
LIMIT 50 