select data_date, avg(temp2), avg(soil), max(soil)-min(soil), avg(soil1), avg(soil2), avg(soil3) from environment where data_date between '2023-04-16 18:00' and '2023-04-16 19:00';
