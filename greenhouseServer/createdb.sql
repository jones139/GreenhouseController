create table environment (
       data_date datetime,
       temp1 real,
       temp2 real,
       rh real,
       light real,
       soil int);
create table water (
       data_date datetime,
       waterStatus int,
       onTime int,
       cycleTime int,
       setpoint real,
       Kp real,
       Ki real,
       Kd real);
       
