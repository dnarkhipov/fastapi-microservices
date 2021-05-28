import json
from datetime import datetime, timedelta, timezone

import asyncpg
from asyncpg.pool import Pool


async def init_connection(conn):
    def tstz_encoder(tstz):
        return [
            (
                tstz.astimezone() - datetime(2000, 1, 1, tzinfo=timezone.utc)
            ).total_seconds()
            * 1000000
        ]

    def tstz_decoder(tup):
        return (
            datetime(2000, 1, 1, tzinfo=timezone.utc) + timedelta(microseconds=tup[0])
        ).astimezone()

    # https://github.com/MagicStack/asyncpg/issues/140
    # https://github.com/MagicStack/asyncpg/issues/221
    await conn.set_type_codec(
        "timestamptz",
        encoder=tstz_encoder,
        decoder=tstz_decoder,
        format="tuple",
        schema="pg_catalog",
    )
    await conn.set_type_codec(
        "jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
    )
    await conn.set_type_codec(
        "json", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
    )


async def connect_to_db(dsn: str) -> Pool:
    connection_pool = await asyncpg.create_pool(
        dsn, min_size=10, max_size=10, init=init_connection
    )
    return connection_pool
