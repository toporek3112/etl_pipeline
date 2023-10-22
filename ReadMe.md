# NYC Street Accidents Dataset
This readme describes how to setup a ETL proess on the dataset [Motor Vehicle Collisions - Crashes](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95)

## Overview
Overall this repo one python scripts which are responsible for handling the ETL process:

* run_etl.py

After the data has been aquired and processed it is ready to be visualized. In this case Grafana was choosen as the one to go with. Althou Grafana is not a common BI tool and is mostly used for monitoring purposes it also can connect to datasources like PostgreSQL. This allows makes it possible to query and visualize the data which was prepared in the ETL process.

## Prerequisite
* docker installed
* docker-compose installed

## Setup
Before starting the ETL process the database and Grafana need to be setup. 

Without persisting the database
```console
docker-compose up -d
```

With persisting the database
```console
docker-compose -f docker-compose.yaml -f docker-compose.overwrite.yaml up -d
```

Note: if you want persistence make sure to create /tmp/postgres beforehand

| Service | URL                   |
| ------- | --------------------- |
| Grafana | http://localhost:3000 |
| pgAdmin | http://localhost:5050 |

check if containers are running
```console
docker ps
CONTAINER ID   IMAGE            ...  COMMAND                 NAMES
fcad8de55573   postgres:latest  ...  "docker-entrypoint.s…"  postgres
5150b51d754e   grafana/grafana  ...  "/run.sh"               grafana
2aac06afdf10   dpage/pgadmin4   ...  "/entrypoint.sh"        pgadmin
```

Connect to PostgreSQL via docker
```console
docker run --rm --link postgres:postgres -it postgres psql -h postgres -U postgres -d postgres
```

Get postgres IP so you can connect to it in pgAdmin and Grafana
```console
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' postgres
```

## ETL Process
When the database is ready it is time to start with the ETL process

1. Execute script:
```console
python3 run_etl.py
```

After running this script it will ask for user input for choosing a dataset to perform the etl process

## Visualization

Grafana: http://localhost:3000
