drop function constructor_victories_count(constructor_name varchar);
create function constructor_victories_count(constructor_name varchar) returns bigint
language plpgsql
as
$$
    declare
        victories bigint;
begin
    select count into victories from (
                select constructors.constructorref, races.year, COUNT(*) count
                    from results
                    join races on races.RaceID = results.RaceID
                    join constructors on constructors.ConstructorID = results.ConstructorID
                    where results.Position = 1
                    group by grouping sets (races.Year, constructors.constructorref)
                    order by races.Year
            ) result
    where result.constructorref = constructor_name;
    return victories;
end;
$$;

drop function constructors_drivers_count(constructor_name varchar);
create function constructors_drivers_count(constructor_name varchar) returns bigint
language plpgsql
as
$$
    declare
        drivers_count bigint;
begin
    select count(*) into drivers_count  from (
        select  d.driverid driver_id, concat(d.forename, ' ',d.surname) driver_name, count(*)
            from results
            join constructors c on c.constructorid = results.constructorid and c.constructorref = constructor_name
            join driver d on results.driverid = d.driverid
        group by grouping sets (d.driverid)
        order by (d.driverid)
    ) result;
    return drivers_count;
end;
$$;

drop function constructors_first_and_last_year(constructor_name varchar, first_year int, last_year int);
create function constructors_first_and_last_year(constructor_name varchar, out first_year int, out last_year int) returns setof record
language plpgsql
as

$$
begin
    return query (
        select min(r.year) , max(r.year)
            from results
            join constructors c on c.constructorid = results.constructorid and c.constructorref = constructor_name
            join races r on results.raceid = r.raceid
        );
end;
$$;

