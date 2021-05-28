-- name: up#
create or replace function update_commands_record() returns trigger
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

create table commands
(
	id bigserial,
	equipment_id bigint not null,
	toc_id bigint not null,
	name varchar(30) not null,
	name_full varchar(150) not null,
	description varchar(300) not null,
	undo_cmd_id bigint,
	archive boolean default false not null,
	create_dt timestamp with time zone default now() not null,
	update_dt timestamp with time zone default now() not null,
	constraint commands_pk primary key (id),
	constraint commands_toc_fk foreign key (toc_id) references commands_toc(id),
    constraint commands_undo_fk foreign key (undo_cmd_id) references commands(id)
);

comment on table commands is 'команды управления';

comment on column commands.equipment_id is 'ссылка на объект, к которому относится команда (см. equipment)';

comment on column commands.toc_id is 'тип по каталогу (см. commands_toc)';

comment on column commands.name is 'код (номер) команды';

comment on column commands.name_full is 'полное наименование команды';

comment on column commands.description is 'описание (действие) команды';

comment on column commands.undo_cmd_id is 'ссылка на команду отмены';

comment on column commands.archive is 'признак архивной записи';

comment on column commands.create_dt is 'время создания записи';

comment on column commands.update_dt is 'время последнего обновления записи';

create unique index commands_name_uindex
	on commands (name);

create trigger commands_tgr
	before update
	on commands
	for each row
	execute procedure update_commands_record();

-- Резерв
INSERT INTO commands("name", "name_full", "description", "equipment_id", "toc_id") VALUES('R105', 'Резерв', 'Резерв', 4, 5);
INSERT INTO commands("name", "name_full", "description", "equipment_id", "toc_id") VALUES('R106', 'Резерв', 'Резерв', 4, 5);
INSERT INTO commands("name", "name_full", "description", "equipment_id", "toc_id") VALUES('R107', 'Резерв', 'Резерв', 4, 5);
INSERT INTO commands("name", "name_full", "description", "equipment_id", "toc_id") VALUES('R115', 'Резерв', 'Резерв', 4, 5);


-- Задана команда отмены
update commands set "undo_cmd_id" = (select id from commands where name = 'R' || '105') where name = 'R106';
update commands set "undo_cmd_id" = (select id from commands where name = 'R' || '115') where name = 'R107';


-- name: down#
drop table if exists commands;
drop function if exists update_commands_record();
