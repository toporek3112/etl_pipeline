# run postgres in docker
docker run --name postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=postgres -p 5432:5432 -d postgres:latest
# run pgAdmin 
docker run -p 5050:80 \
    -e 'PGADMIN_DEFAULT_EMAIL=user@example.com' \
    -e 'PGADMIN_DEFAULT_PASSWORD=postgres' \
    --name pgadmin4_container \
    -d dpage/pgadmin4
# http://localhost:5050

# connect to postgres container
docker run --rm --link postgres:postgres -it postgres psql -h postgres -U postgres -d postgres

# create db tables 
docker run --rm --link postgres:postgres -v $(pwd)/data:/tmp -it postgres psql -h postgres -U postgres -d postgres -a -f /tmp/db.sql

