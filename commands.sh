# run postgres in docker
docker run --name postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=postgres -p 5432:5432 -d postgres:latest
# run pgAdmin 
docker run -p 5050:80 \
    -e 'PGADMIN_DEFAULT_EMAIL=admin@admin.com' \
    -e 'PGADMIN_DEFAULT_PASSWORD=postgres' \
    --name pgadmin \
    -d dpage/pgadmin4
# http://localhost:5050

# get postgres ip
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' postgres

# connect to postgres
docker run --rm --link postgres:postgres -it postgres psql -h postgres -U postgres -d postgres
pgcli -h localhost -U postgres -d postgres

# create db tables 
docker run --rm --link postgres:postgres -v $(pwd)/data:/tmp -it postgres psql -h postgres -U postgres -d postgres -a -f /tmp/db.sql


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

Select 