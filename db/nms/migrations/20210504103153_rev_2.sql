-- name: up#
create or replace function update_commands_toc_record() returns trigger
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


create table commands_toc
(
	id bigserial not null
		constraint commands_toc_pk
			primary key,
	parent_id bigint,
	name varchar(120) not null,
	parent_path ltree,
	parent_path_name varchar(400),
	archive boolean default false not null,
	create_dt timestamp with time zone default now() not null,
	update_dt timestamp with time zone default now() not null
);

comment on table commands_toc is 'каталог команд управления';

comment on column commands_toc.parent_id is 'ссылка на родительскую запись';

comment on column commands_toc.name is 'наименование раздела';

comment on column commands_toc.parent_path is 'полный путь до родительской записи (id)';

comment on column commands_toc.parent_path_name is 'полный путь до родительской записи (name)';

comment on column commands_toc.archive is 'признак архивной записи';

comment on column commands_toc.create_dt is 'время создания записи';

comment on column commands_toc.update_dt is 'время последнего обновления записи';


create unique index commands_toc_name_uindex
	on commands_toc (parent_path, name);


create trigger commands_toc_tgr
	before insert or update
	on commands_toc
	for each row
	execute procedure update_commands_toc_record();

INSERT INTO commands_toc("name", parent_id) VALUES('Аппаратные команды Service #1', NULL);
INSERT INTO commands_toc("name", parent_id) VALUES('Аппаратные команды Service #2', NULL);
INSERT INTO commands_toc("name", parent_id) VALUES('Аппаратные команды Service #3', NULL);

INSERT INTO commands_toc("name", parent_id) VALUES('Команды аварийного отключения', 1);
INSERT INTO commands_toc("name", parent_id) VALUES('Кодовые команды управления оборудования Service #1', 1);
INSERT INTO commands_toc("name", parent_id) VALUES('Команды управления оборудованием Service #1 по TCP/IP', 1);
INSERT INTO commands_toc("name", parent_id) VALUES('Команды по управлению Service #1.FPGA', 1);
INSERT INTO commands_toc("name", parent_id) VALUES('Команды загрузки данных управления', 1);


-- name: down#
drop table if exists commands_toc;
drop function if exists update_commands_toc_record();
