# NYC Street Accidents Dataset
This readme describes how to setup a ETL proess on the dataset [Motor Vehicle Collisions - Crashes](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95)

## Overview
Overall this repo contains three python scripts which are responsible for handling the ETL process:

* 01_insertIntoStagingTable.py
  * Fetches data from the Socrata API 
  * Removes whitespaces from strings
  * And saves it into the staging table
* 02_prepareForCorrection
  * Prepares two csv files in the /data folder (stagingContributingFactorsCorrected.csv, stagingVehicleTypesCorrected.csv) for correction (must be done manually)
* 03_insertIntoTables
  * Inserts corrected data from the staging table into the respective dimension and fact tables

After the data has been aquired and processed it is ready to be visualized. In this case Grafana was choosen as the one to go with. Althou Grafana is not a common BI tool and is mostly used for monitoring purposes it also can connect to datasources like PostgreSQL. This allows makes it possible to query and visualize the data which was prepared in the ETL process.

## Prerequisite
* docker installed
* docker-compose installed

## Setup
Before starting the ETL process the database and Grafana need to be setup. 

```console
docker-compose up -d # no persistence 
docker-compose -f docker-compose.yaml -f docker-compose.overwrite.yaml up -d # with persistence
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

Create Database 
```console
docker run --rm --link postgres:postgres -v $(pwd)/data/database:/tmp -it postgres psql -h postgres -U postgres -a -f /tmp/create_db.sql
```

Create Tables 
```console
docker run --rm --link postgres:postgres -v $(pwd)/data/database:/tmp -it postgres psql -h postgres -U postgres -d nyc_motor_vechicle_collisions -a -f /tmp/create_tables.sql
```

Connect to PostgreSQL via docker
```console
docker run --rm --link postgres:postgres -it postgres psql -h postgres -U postgres -d postgres
pgcli -h localhost -U postgres -d postgres
```

Get postgres IP so you can connect to it in pgAdmin and Grafana
```console
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' postgres
```

## ETL Process
When the database is ready it is time to start with the ETL process

1. Execute first script:
```console
python3 01_insertIntoStagingTable.py
```
Note: This script can take up to ~30min to fetch, clear and insert the data to the staging table

2. Execute second script:
```console
python3 02_prepareForCorrection.py
```

After this script finishes it creates two new files in the data folder:
* stagingContributingFactorsCorrected.csv
* stagingVehicleTypesCorrected.csv

These csv files have to columns 'original' and 'corrected'. Before the ETL process can proceed it is advised to go throug the files and check for any inconsistencies which can be corrected. Simply put a value into the 'corrected' column and the original value will be replaced in the next step when writing to the respective dimension and fact tables.

3. Execute thrid script
```console
python3 03_insertIntoTables.py
```
This script is the final one and inserts the data from the staging tabe to the dimension and fact tables. 
Note: this script can also take up to ~30min

## Visualization

Grafana: http://localhost:3000
