#!/bin/bash

set -e

# DEV
psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" <<-EOSQL
  -- auth
	create role auth login password 'auth';
	create database auth owner auth;
	-- nms
	create role nms login password 'nms';
	create database nms owner nms;
	\c nms
	create extension if not exists "ltree";
	create extension if not exists "uuid-ossp";
	-- admin
	create role admin login password 'admin';
	create database admin owner admin;
	-- dwh
	create role dwh login password 'dwh';
	create database dwh owner dwh;
	\c dwh
	create extension if not exists "ltree";
	create extension if not exists "uuid-ossp";
EOSQL
