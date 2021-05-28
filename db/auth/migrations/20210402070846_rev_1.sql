-- name: up#
create table user_roles
(
	id varchar(80) not null
		constraint user_roles_pk
			primary key,
	description varchar(80) not null,
	access bigint default 0 not null
);

comment on column user_roles.id is 'уникальный идентификатор роли';

comment on column user_roles.description is 'наименование роли (русский)';

comment on column user_roles.access is 'доступы для роли (битовая маска)';


-- Предустановленные роли
INSERT INTO public.user_roles (id, description, "access") VALUES('administrator', 'Администратор', 4227858455);

create table users
(
	id bigserial not null
		constraint users_pk
			primary key,
	login varchar(50) not null
		constraint users_login
			unique,
	name varchar(80) not null,
	password varchar(60) not null,
	role_id varchar(80) not null
		constraint users_fk
			references user_roles,
	status smallint default 0 not null,
	create_dt timestamp with time zone default now() not null,
	update_dt timestamp with time zone default now() not null,
	dark_theme boolean default false not null
);

comment on column users.login is 'логин';

comment on column users.name is 'ФИО пользователя';

comment on column users.password is 'хэш пароля (bcrypt)';

comment on column users.role_id is 'ссылка на роль (см. auth_roles)';

comment on column users.status is 'статус: -1 - архивирован; 0 - включен; 1 - блокирован';

comment on column users.create_dt is 'дата создания записи';

comment on column users.update_dt is 'дата последнего обновления записи';

comment on column users.dark_theme is 'Пользовательская тема (dark-light)';

-- Пользователи по умолчанию:
-- user_super | user_super
INSERT INTO public.users (login, name, password, role_id)
 VALUES ('admin_nms', 'Иванов И.И.', '$2b$12$SSG7xbA7Lz5BPWzlFWX.LuFXL2k2SAIGDhZtLitL4xfdQIkq8bz9.', 'administrator');

create table users_history
(
	id bigserial not null
		constraint users_history_pk
			primary key,
	user_id bigint not null
		constraint users_history_fk
			references users,
	name varchar(80) not null,
	password varchar(60) not null,
	role_id varchar(80) not null,
	status smallint default 0 not null,
	fd timestamp with time zone not null,
	td timestamp with time zone not null
);

comment on column users_history.user_id is 'ссылка на актуальную версию (см. users.id)';

comment on column users_history.fd is 'дата начала действия версии';

comment on column users_history.td is 'дата окончания действия версии';


create function log_users_history() returns trigger
	language plpgsql
as $$
begin
new.update_dt = now();
if new.status >= 0 then
insert into public.users_history(user_id, name, password, role_id, status, fd, td)
values(old.id, old.name, old.password, old.role_id, old.status, old.update_dt, NEW.update_dt - interval '1 second');
else
new.login = old.login || '-' || to_char(new.update_dt, 'YYYYMMDDHH24MISS');
end if;
RETURN NEW;
END;
$$;

create trigger update_users_before
	before update
	on users
	for each row
	execute procedure log_users_history();

-- name: down#
drop table if exists public.users_history;
drop table if exists public.users;
drop table if exists public.user_roles;
drop function if exists public.log_users_history();
