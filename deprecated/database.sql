create table if not exists public."Coordinates"
(
    "CoordinateId" integer not null
        constraint "Coordinates_pk"
            primary key,
    "Latitude"     double precision,
    "Longitude"    double precision
);

alter table public."Coordinates"
    owner to postgres;

create table if not exists public."Addresses"
(
    "AddressId"       integer not null
        constraint "Adresses_pk"
            primary key,
    "Borough"         varchar(255),
    "ZIPCode"         integer,
    "OnStreetName"    varchar(255),
    "CrossStreetName" varchar(255),
    "OffStreetName"   varchar(255)
);

alter table public."Addresses"
    owner to postgres;

create table if not exists public."Timestamps"
(
    "TimestampId" integer not null
        constraint "Timestamps_pk"
            primary key,
    "Hour"        integer,
    "Day"         integer,
    "Month"       integer,
    "Year"        integer,
    "DateObj"     timestamp
);

alter table public."Timestamps"
    owner to postgres;

create table if not exists public."Vehicles"
(
    "VehicleId" integer not null
        constraint "Vehicles_pk"
            primary key,
    "Type"      varchar(255)
);

alter table public."Vehicles"
    owner to postgres;

create table if not exists public."ContributingFactors"
(
    "ContributingFactorId" integer not null
        constraint "ContributingFactors_pk"
            primary key,
    "ContributingFactor"   varchar(255)
);

alter table public."ContributingFactors"
    owner to postgres;

create table if not exists public."Accidents"
(
    "CollisionId"           integer not null,
    "NrVehicles"            integer,
    "NrVictims"             integer,
    "TimestampId"           integer
        constraint "Timestamp"
            references public."Timestamps",
    "AddressId"             integer
        constraint "Adress"
            references public."Addresses",
    "CoordinateId"          integer
        constraint "Coordinate"
            references public."Coordinates",
    "Vehicle1Id"            integer
        constraint "Vehicle1"
            references public."Vehicles",
    "Vehicle2Id"            integer
        constraint "Vehicle2"
            references public."Vehicles",
    "Vehicle3Id"            integer
        constraint "Vehicle3"
            references public."Vehicles",
    "Vehicle4Id"            integer
        constraint "Vehicle4"
            references public."Vehicles",
    "Vehicle5Id"            integer
        constraint "Vehicle5"
            references public."Vehicles",
    "NrInjured"             integer,
    "NrKilled"              integer,
    "ContributingFactor1Id" integer
        constraint "ContributingFactor1"
            references public."ContributingFactors",
    "ContributingFactor2Id" integer
        constraint "ContributingFactor2"
            references public."ContributingFactors",
    "ContributingFactor3Id" integer
        constraint "ContributingFactor3"
            references public."ContributingFactors",
    "ContributingFactor4Id" integer
        constraint "ContributingFactor4"
            references public."ContributingFactors",
    "ContributingFactor5Id" integer
        constraint "ContributingFactor5"
            references public."ContributingFactors",
    "AccidentId"            integer not null
        constraint "Accidents_pk"
            primary key
);

alter table public."Accidents"
    owner to postgres;

create table if not exists public."Staging"
(
    crash_date                    date,
    crash_time                    varchar(255),
    borough                       varchar(255),
    zip_code                      varchar(255),
    latitude                      double precision,
    longitude                     double precision,
    on_street_name                varchar(255),
    off_street_name               varchar(255),
    number_of_persons_injured     integer,
    number_of_persons_killed      integer,
    number_of_pedestrians_injured integer,
    number_of_pedestrians_killed  integer,
    number_of_cyclist_injured     integer,
    number_of_cyclist_killed      integer,
    number_of_motorist_injured    integer,
    number_of_motorist_killed     integer,
    contributing_factor_vehicle_1 varchar(255),
    contributing_factor_vehicle_2 varchar(255),
    contributing_factor_vehicle_3 varchar(255),
    contributing_factor_vehicle_4 varchar(255),
    contributing_factor_vehicle_5 varchar(255),
    collision_id                  integer,
    vehicle_type_code_1           varchar(255),
    vehicle_type_code_2           varchar(255),
    vehicle_type_code_3           varchar(255),
    vehicle_type_code_4           varchar(255),
    vehicle_type_code_5           varchar(255),
    cross_street_name             varchar(255)
);

alter table public."Staging"
    owner to postgres;

