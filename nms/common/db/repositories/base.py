from asyncpg.connection import Connection

from nms.common.config import DSNType


class BaseRepository:
    _dsn_type = DSNType.UNKNOWN

    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    @property
    def connection(self) -> Connection:
        return self._conn

    @classmethod
    def dsn_type(cls) -> DSNType:
        return cls._dsn_type


class BaseNmsRepository(BaseRepository):
    _dsn_type = DSNType.NMS


class BaseAuthRepository(BaseRepository):
    _dsn_type = DSNType.AUTH


class BaseDwhRepository(BaseRepository):
    _dsn_type = DSNType.DWH


class BaseAdminRepository(BaseRepository):
    _dsn_type = DSNType.ADMIN
