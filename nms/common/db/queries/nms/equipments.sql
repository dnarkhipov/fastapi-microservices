-- name: get_equipment_by_id^
-- record_class: EquipmentInDb
select e.id,
       e.parent_id,
       e.parent_path,
       e.parent_path_name,
       e.name,
       e.name_full,
       e.create_dt,
       e.update_dt
from equipment e
where e.id = :equipment_id
  and not e.archive;


-- name: get_equipment_by_name^
-- record_class: EquipmentInDb
select e.id,
       e.parent_id,
       e.parent_path,
       e.parent_path_name,
       e.name,
       e.name_full,
       e.create_dt,
       e.update_dt
from equipment e
where lower(e.name) = lower(:name)
  and not e.archive;


-- name: get_equipments_all
-- record_class: EquipmentInDb
select e.id,
       e.parent_id,
       e.parent_path,
       e.parent_path_name,
       e.name,
       e.name_full,
       e.create_dt,
       e.update_dt
from equipment e
where not e.archive
order by e.parent_path;


-- name: get_equipments_from
-- record_class: EquipmentInDb
select e.id,
       e.parent_id,
       e.parent_path,
       e.parent_path_name,
       e.name,
       e.name_full,
       e.create_dt,
       e.update_dt
from equipment e
where not e.archive
  and e.parent_path || e.id::text <@ (select parent_path || id::text
                                           from equipment
                                           where id = :equipment_id
                                             and not archive)
order by e.parent_path;


-- name: create_equipment<!
insert into equipment (parent_id, name, name_full)
values (:parent_id, :name, :name_full)
ON CONFLICT DO NOTHING
returning
    id,
    parent_id,
    parent_path,
    parent_path_name,
    name,
    name_full,
    create_dt,
    update_dt;


-- name: delete_equipment<!
with dst_equipment as (
    select id
    from equipment d
    where d.id = :equipment_id
      and not d.archive
      and not exists(select t.id from equipment t where t.parent_id = d.id and not t.archive)
)
update equipment
set archive = true
where id in (select id from dst_equipment)
returning id;


-- name: delete_equipment_recursive<!
with dst_equipment as (
    select id
    from equipment
    where not archive
      and parent_path || id::text <@
          (select parent_path || id::text
           from equipment
           where id = :equipment_id
             and not archive)
)
update equipment
set archive = true
where id in (select id from dst_equipment)
returning id;


-- name: update_equipment<!
update equipment
set parent_id = :parent_id,
    name = :name,
    name_full = :name_full
where id = :equipment_id
  and not archive
returning
    id,
    parent_id,
    parent_path,
    parent_path_name,
    name,
    name_full,
    create_dt,
    update_dt;
