###auth

    cd auth

    aiosqlembic --debug -m ./migrations asyncpg postgres://auth:auth@localhost:5432/auth create -n "rev 1"
    aiosqlembic --debug -m ./migrations asyncpg postgres://auth:auth@localhost:5432/auth status

###nms

    cd nms

    aiosqlembic --debug -m ./migrations asyncpg postgres://nms:nms@localhost:5432/nms create -n "rev 1"
    aiosqlembic --debug -m ./migrations asyncpg postgres://nms:nms@localhost:5432/nms status
