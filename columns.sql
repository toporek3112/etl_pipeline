create table "Staging";
alter table "Staging" add crash_date date;
alter table "Staging" add crash_time varchar(255);
alter table "Staging" add borough varchar(255);
alter table "Staging" add zip_code varchar(255);
alter table "Staging" add latitude varchar(255);
alter table "Staging" add longitude varchar(255);
alter table "Staging" add on_street_name varchar(255);
alter table "Staging" add off_street_name varchar(255);
alter table "Staging" add number_of_persons_injured varchar(255);
alter table "Staging" add number_of_persons_killed varchar(255);
alter table "Staging" add number_of_pedestrians_injured varchar(255);
alter table "Staging" add number_of_pedestrians_killed varchar(255);
alter table "Staging" add number_of_cyclist_injured varchar(255);
alter table "Staging" add number_of_cyclist_killed varchar(255);
alter table "Staging" add number_of_motorist_injured varchar(255);
alter table "Staging" add number_of_motorist_killed varchar(255);
alter table "Staging" add contributing_factor_vehicle_1 varchar(255);
alter table "Staging" add contributing_factor_vehicle_2 varchar(255);
alter table "Staging" add collision_id varchar(255);
alter table "Staging" add vehicle_type_code_1 varchar(255);
alter table "Staging" add vehicle_type_code_2 varchar(255);
alter table "Staging" add contributing_factor_vehicle_3 varchar(255);
alter table "Staging" add vehicle_type_code_3 varchar(255);
alter table "Staging" add contributing_factor_vehicle_4 varchar(255);
alter table "Staging" add vehicle_type_code_4 varchar(255);
alter table "Staging" add cross_street_name varchar(255);
alter table "Staging" add contributing_factor_vehicle_5 varchar(255);
alter table "Staging" add vehicle_type_code_5 varchar(255);
