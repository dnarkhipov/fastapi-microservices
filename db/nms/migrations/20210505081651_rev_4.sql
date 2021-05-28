-- name: up#
create or replace function update_telemetry_record() returns trigger
    language plpgsql
as
$$
begin
    new.update_dt = now();
    if new.archive = true then
        new.name = old.name || '-' || to_char(new.update_dt, 'YYYYMMDDHH24MISS');
    end if;
    return new;
end;
$$;

create table telemetry
(
	id bigserial not null
		constraint telemetry_pk
			primary key,
	name varchar(80) not null,
	name_full varchar(200) not null,
	description varchar(300) not null,
	value_validator jsonb not null,
    archive boolean default false not null,
	create_dt timestamp with time zone default now() not null,
	update_dt timestamp with time zone default now() not null
);

comment on table telemetry is 'параметры телеметрии';

comment on column telemetry.name is 'обозначение (индекс)';

comment on column telemetry.name_full is 'наименование';

comment on column telemetry.description is 'описание';

comment on column telemetry.value_validator is 'формат значения параметра (JSON Schema)';

comment on column telemetry.archive is 'признак архивной записи';

comment on column telemetry.create_dt is 'время создания записи';

comment on column telemetry.update_dt is 'время последнего обновления записи';

create unique index telemetry_name_uindex
	on telemetry (name);

create trigger telemetry_tgr
	before update
	on telemetry
	for each row
	execute procedure update_telemetry_record();

-- ТМИ
INSERT INTO telemetry (name, name_full, description, value_validator) VALUES ('tmi1', 'ВКЛ/ОТКЛ всех модулей Service 1', 'Статус ВКЛ/ОТКЛ всех модулей Service 1', '{"length": 16, "parser": "TmCommonParser"}');
INSERT INTO telemetry (name, name_full, description, value_validator) VALUES ('tmi2', 'ВКЛ/ОТКЛ всех модулей Service 2', 'Статус ВКЛ/ОТКЛ всех модулей Service 1', '{"length": 16, "parser": "TmCommonParser"}');
INSERT INTO telemetry (name, name_full, description, value_validator) VALUES ('tmi3', 'Пров.контр.суммы  Application EEPROM', 'Проверка контрольной суммы Application EEPROM', '{"length": 1, "parser": "TmCommonParser"}');
INSERT INTO telemetry (name, name_full, description, value_validator) VALUES ('tmi4', 'Пров.при копир.Application EEPROM в RAM', 'Проверка при копировании Application EEPROM в RAM', '{"length": 1, "parser": "TmCommonParser"}');


-- name: down#
drop table if exists telemetry;
drop function if exists update_telemetry_record();
