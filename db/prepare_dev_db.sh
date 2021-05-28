#!/bin/bash

set -e

aiosqlembic -m ./auth/migrations asyncpg postgres://auth:auth@localhost:5432/auth up
aiosqlembic -m ./nms/migrations asyncpg postgres://nms:nms@localhost:5432/nms up
