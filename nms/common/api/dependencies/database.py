from typing import TYPE_CHECKING, AsyncGenerator, Callable, Type

if TYPE_CHECKING:
    from nms.common.service import CoreService

from asyncpg.connection import Connection as PgConnection
from asyncpg.pool import Pool as PgPool
from fastapi import Depends, Request, WebSocket

from nms.common.config import DSNType
from nms.common.db.repositories.base import BaseRepository


class RepositoryConnectionRouter:
    def __init__(self, repo_type: Type[BaseRepository]):
        self.dsn_type = repo_type.dsn_type()  # type: DSNType

    async def __call__(
        self, request: Request = None, websocket: WebSocket = None
    ) -> AsyncGenerator[PgConnection, None]:
        core_service = (
            request.app.state.core if request else websocket.app.state.core
        )  # type: CoreService
        pool = core_service.get_connection_pool(self.dsn_type)  # type: PgPool
        async with pool.acquire() as conn:
            yield conn


def get_db_repository(
    repo_type: Type[BaseRepository],
) -> Callable[[PgConnection], BaseRepository]:
    def get_repo(
        conn: PgConnection = Depends(RepositoryConnectionRouter(repo_type)),
    ) -> BaseRepository:
        return repo_type(conn)

    return get_repo
