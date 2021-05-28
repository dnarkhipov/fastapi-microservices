-- name: up#
create or replace function update_equipment_record() returns trigger
    language plpgsql
as
$$
DECLARE
    path_id   ltree;
    path_name varchar(400);
begin
    if TG_OP = 'UPDATE' then
        new.update_dt = now();
        if new.archive = true then
			new.name = old.name || '-' || to_char(new.update_dt, 'YYYYMMDDHH24MISS');
		end if;
    end if;
    IF NEW.parent_id IS NULL THEN
        NEW.parent_path = '0'::ltree;
        NEW.parent_path_name = '/';
    ELSE
        execute format('SELECT parent_path || id::text FROM %I WHERE id = $1', TG_TABLE_NAME) INTO path_id using NEW.parent_id;
        IF path_id IS NULL THEN
            RAISE EXCEPTION 'Invalid parent_id %', NEW.parent_id;
        END IF;
        execute format('SELECT CASE WHEN parent_path_name = ''/'' THEN parent_path_name || "name" ELSE parent_path_name || ''/'' || "name" END FROM %I WHERE id = $1', TG_TABLE_NAME) INTO path_name using NEW.parent_id;
        NEW.parent_path = path_id;
        NEW.parent_path_name = path_name;
    END IF;
    RETURN NEW;
END;
$$;

create table equipment
(
	id bigserial not null
		constraint equipment_pk
			primary key,
	parent_path ltree not null,
	parent_path_name varchar(400) not null,
	parent_id bigint
		constraint equipment_parent_id_fkey
			references equipment,
	name varchar(70) not null,
	name_full varchar(150) not null,
	archive boolean default false not null,
	create_dt timestamp with time zone default now() not null,
	update_dt timestamp with time zone default now() not null
);

comment on column equipment.id is 'идентификатор объекта';

comment on column equipment.parent_path is 'полный путь до родительского объекта';

comment on column equipment.parent_path_name is 'полный путь до родительского объекта (name)';

comment on column equipment.parent_id is 'ссылка на родительский объект';

comment on column equipment.name is 'обозначение на схеме';

comment on column equipment.name_full is 'наименование';

comment on column equipment.archive is 'признак архивной записи';

comment on column equipment.create_dt is 'время создания записи';

comment on column equipment.update_dt is 'время последнего обновления записи';

create index equipment_parent_id_idx
	on equipment (parent_id);

create index equipment_path_idx
	on equipment using gist (parent_path);

create unique index equipment_name_uindex
	on equipment (name);

create trigger equipment_tgr
	before insert or update
	on equipment
	for each row
	execute procedure update_equipment_record();


INSERT INTO public.equipment ("name", name_full, parent_id) VALUES('ROOT_Object', 'ROOT_Object', NULL);
INSERT INTO public.equipment ("name", name_full, parent_id) VALUES('Service_Core', 'Service_Core', 1);
INSERT INTO public.equipment ("name", name_full, parent_id) VALUES('Service_Support', 'Service_Support', 1);
INSERT INTO public.equipment ("name", name_full, parent_id) VALUES('Service1', 'Customer Service #1', 2);
INSERT INTO public.equipment ("name", name_full, parent_id) VALUES('Service2', 'Customer Service #2', 2);
INSERT INTO public.equipment ("name", name_full, parent_id) VALUES('Service3', 'Customer Service #3', 2);
INSERT INTO public.equipment ("name", name_full, parent_id) VALUES('Service1_1', 'Customer Service #1.1', 4);
INSERT INTO public.equipment ("name", name_full, parent_id) VALUES('Service1_2', 'Customer Service #1.2', 4);
INSERT INTO public.equipment ("name", name_full, parent_id) VALUES('Service1_3', 'Customer Service #1.3', 4);
INSERT INTO public.equipment ("name", name_full, parent_id) VALUES('Service1_4', 'Customer Service #1.4', 4);
INSERT INTO public.equipment ("name", name_full, parent_id) VALUES('Service_Control_1', 'Service Control #1', NULL);


-- name: down#
drop table if exists equipment;
drop function if exists update_equipment_record();
