# NYC Street Accidents Dataset
This readme describes how to setup a ETL proess on the dataset [Motor Vehicle Collisions - Crashes](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95)

## Overview
Overall this repo contains three python scripts which are responsible for handling the ETL process:

* 01_insertIntoStagingTable.py
  * Fetches filtered data from the Socrata API 
  * Removes whitespaces from strings
  * And saves it into the staging table
* 02_prepareForCorrection
  * Prepares two csv files in the /data folder (stagingContributingFactorsCorrected.csv, stagingVehicleTypesCorrected.csv) for correction
* 03_insertIntoTables
  * Inserts corrected data from the staging table into the respective dimension and fact tables

## Prerequisite
* docker installed

## Setup
Before you can start the ETL process the database needs to be setup.

Start PostgreSQL 
```console
docker run --name postgres -p 5432:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=postgres -d postgres:latest
```

Create Database 
```console
docker run --rm --link postgres:postgres -v $(pwd)/data:/tmp -it postgres psql -h postgres -U postgres -a -f /tmp/create_db.sql
```

Create Tables 
```console
docker run --rm --link postgres:postgres -v $(pwd)/data:/tmp -it postgres psql -h postgres -U postgres -d nyc_motor_vechicle_collisions -a -f /tmp/create_tables.sql
```

Connect to PostgreSQL via docker
```console
docker run --rm --link postgres:postgres -it postgres psql -h postgres -U postgres -d postgres
pgcli -h localhost -U postgres -d postgres
```

### Optional
Start pgAdmin
```console
docker run --name pgadmin -p 5050:80  -e 'PGADMIN_DEFAULT_EMAIL=admin@admin.com' -e 'PGADMIN_DEFAULT_PASSWORD=postgres' -d dpage/pgadmin4
```
pgAdmin: http://localhost:5050

Get postgres IP so you can connect to it in pgAdmin
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

After this script finishes you should see two new files in the data folder:
* stagingContributingFactorsCorrected.csv
* stagingVehicleTypesCorrected.csv

These csv files have to columns 'original' and 'corrected'. Before you can proceed with the ETL process it is advised to go throug them and check for any inconsistencies which can be corrected. Simply put a value into the 'corrected' column and the original value will be replaced in the next step when writing to the respective dimension and fact tables.

3. Execute thrid script
```console
python3 03_insertIntoTables.py
```
This script is the final one and inserts the data from the staging tabe to the dimension and fact tables. 
Note: this script can also take up to ~30min

## Visualization
For visualization we have chosen a simple yet good enought approche using Grafana. Althou Grafana is not a common BI tool and is mostly used for monitoring purposes it also can connect to datasources like PostgreSQL. This allows us to query and visualize the data which we prepared in the ETL process.

Start Grafana
```console
docker run -d --name=grafana -p 3000:3000 -e GF_SECURITY_ADMIN_USER=postgres -e GF_SECURITY_ADMIN_PASSWORD=postgres grafana/grafana
```
Grafana: http://localhost:3000

First thing to do in Grafana is to setup the postgres Datasource. Go to: Connections > Add new connection > select PostgreSQL > create new datasource. Here input the postgres IP and Port (see command above), input the correct database (nyc_motor_vechicle_collisions), the user (postgres) and disable TLS/SSL Mode.

After that to click the button on the top right corner and click import dashboard.
There you select a file from the data folder or paste in the json.