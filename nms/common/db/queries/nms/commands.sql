-- name: get_commands_toc_all
-- record_class: CommandsTocInDb
select id, parent_id, name, parent_path, parent_path_name, create_dt, update_dt
from commands_toc
where not archive
order by parent_path;


-- name: get_commands_toc_by_id^
-- record_class: CommandsTocInDb
select id, parent_id, name, parent_path, parent_path_name, create_dt, update_dt
from commands_toc
where id = :toc_id
  and not archive;


-- name: create_commands_toc<!
insert into commands_toc (parent_id, name)
values (:parent_id, :name)
ON CONFLICT DO NOTHING
returning id, parent_id, name, parent_path, parent_path_name, create_dt, update_dt;


-- name: update_commands_toc<!
update commands_toc
set parent_id = :parent_id,
    name      = :name
where id = :toc_id
  and not archive
returning id, parent_id, name, parent_path, parent_path_name, create_dt, update_dt;


-- name: delete_commands_toc<!
with dst_toc as (
    select id
    from commands_toc d
    where d.id = :toc_id
      and not d.archive
      and not exists(select t.id from commands_toc t where t.parent_id = d.id and not t.archive)
      and not exists(select t.id from commands t where t.toc_id = d.id and not t.archive)
)
update commands_toc
set archive = true
where id in (select id from dst_toc)
returning id;


-- name: get_command_by_id^
-- record_class: CommandInDb
select id,
       equipment_id,
       toc_id,
       name,
       name_full,
       description,
       undo_cmd_id,
       create_dt,
       update_dt
from commands
where id = :command_id
  and not archive;


-- name: get_command_by_name^
-- record_class: CommandInDb
select id,
       equipment_id,
       toc_id,
       name,
       name_full,
       description,
       undo_cmd_id,
       create_dt,
       update_dt
from commands
where lower(name) = lower(:name)
  and not archive;


-- name: create_command<!
insert into commands (equipment_id, toc_id, name, name_full, description, undo_cmd_id)
values (:equipment_id, :toc_id, :name, :name_full, :description, :undo_cmd_id)
ON CONFLICT DO NOTHING
returning id, equipment_id, toc_id, name, name_full, description, undo_cmd_id, create_dt, update_dt;


-- name: update_command<!
update commands
set equipment_id = :equipment_id,
    toc_id       = :toc_id,
    name         = :name,
    name_full    = :name_full,
    description  = :description,
    undo_cmd_id  = :undo_cmd_id
where id = :command_id
  and not archive
returning id, equipment_id, toc_id, name, name_full, description, undo_cmd_id, create_dt, update_dt;


-- name: delete_command<!
with dst as (
    select id
    from commands d
    where d.id = :command_id
      and not d.archive
)
update commands
set archive = true
where id in (select id from dst)
returning id;
