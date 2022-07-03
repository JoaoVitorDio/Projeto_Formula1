create function drivers_victories(driver_forename varchar, driver_surname varchar) returns bigint
language plpgsql
as
$$
    declare
        count bigint;
        driver_id int;
begin
            select driverid into driver_id from driver where forename = driver_forename and surname = driver_surname;

            select count(*) into count
                from results
                join races on results.raceid = races.raceid
                where results.position = 1 and results.driverid = driver_id;

            return count;
end;
$$;


create function drivers_first_and_last_year(driver_forename varchar, driver_surname varchar, out first_year int, out last_year int) returns setof record
language plpgsql
as
$$
    declare
        driver_id int;
begin
    select driverid into driver_id from driver where forename = driver_forename and surname = driver_surname;

    return query (
        select min(r.year) , max(r.year)
            from results
            join races r on results.raceid = r.raceid
            where results.driverid = driver_id
        );
end;
$$;
