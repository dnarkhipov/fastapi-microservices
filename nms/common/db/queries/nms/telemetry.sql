-- name: get_tm_parameter_by_id^
-- record_class: TmParameterInDb
select id,
       name,
       name_full,
       description,
       value_validator,
       create_dt,
       update_dt
from telemetry
where id = :parameter_id
  and not archive;


-- name: get_tm_parameter_by_name^
-- record_class: TmParameterInDb
select id,
       name,
       name_full,
       description,
       value_validator,
       create_dt,
       update_dt
from telemetry
where lower(name) = lower(:name)
  and not archive;


-- name: create_tm_parameter<!
insert into telemetry (name, name_full, description, value_validator)
values (:name, :name_full, :description, :value_validator)
ON CONFLICT DO NOTHING
returning id, name, name_full, description, value_validator, create_dt, update_dt;


-- name: update_tm_parameter<!
update telemetry
set name            = :name,
    name_full       = :name_full,
    description     = :description,
    value_validator = :value_validator
where id = :parameter_id
  and not archive
returning id, name, name_full, description, value_validator, create_dt, update_dt;


-- name: delete_tm_parameter<!
with dst as (
    select id
    from telemetry d
    where d.id = :parameter_id
      and not d.archive
)
update telemetry
set archive = true
where id in (select id from dst)
returning id;
