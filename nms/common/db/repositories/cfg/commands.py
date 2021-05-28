import logging
from typing import List, Optional

from asyncpg import PostgresError

from nms.common.db.errors import (
    ConflictWhenInsert,
    ConflictWhenUpdate,
    EntityDoesNotExist,
)
from nms.common.db.queries.nms import build_queries_search_commands_catalog, queries_nms
from nms.common.db.repositories.base import BaseNmsRepository
from nms.common.models.commands import (
    CommandInCatalogResponse,
    CommandInCreate,
    CommandInDb,
    CommandsTocInCreate,
    CommandsTocInDb,
    CommandsTocInResponse,
)
from nms.common.models.response_pagination import ResponsePage

from .utils import build_catalog

# from aiocache import cached


log = logging.getLogger("app")


class CommandsRepository(BaseNmsRepository):
    async def get_toc_catalog(self) -> list:
        toc = await queries_nms.get_commands_toc_all(self.connection)
        return build_catalog(toc, lambda c: CommandsTocInResponse.from_orm(c).dict())

    async def get_toc(self, toc_id: int) -> CommandsTocInDb:
        toc = await queries_nms.get_commands_toc_by_id(self.connection, toc_id)
        if not toc:
            raise EntityDoesNotExist(f"Command TOC with id={toc_id} does not exists")
        return toc

    async def create_toc(self, toc_data: CommandsTocInCreate) -> CommandsTocInDb:
        try:
            toc = await queries_nms.create_commands_toc(
                self.connection, parent_id=toc_data.parent_id, name=toc_data.name
            )
        except PostgresError as err:
            raise ConflictWhenInsert(
                f"Insert new entity in database raising a unique violation or exclusion constraint violation error: {str(err)}"
            )
        return CommandsTocInDb(**toc)

    async def update_toc(
        self, *, toc: CommandsTocInDb, parent_id: Optional[int], name: Optional[str]
    ) -> CommandsTocInDb:
        toc_update = toc.copy(deep=True)
        toc_update.parent_id = parent_id
        toc_update.name = name or toc.name

        try:
            async with self.connection.transaction():
                toc_update = await queries_nms.update_commands_toc(
                    self.connection,
                    toc_id=toc_update.id,
                    parent_id=toc_update.parent_id,
                    name=toc_update.name,
                )
        except PostgresError as err:
            raise ConflictWhenUpdate(
                f"Insert new entity in database raising a unique violation or exclusion constraint violation error: {str(err)}"
            )
        return CommandsTocInDb(**toc_update)

    async def delete_toc(self, toc: CommandsTocInDb):
        result = await queries_nms.delete_commands_toc(self.connection, toc_id=toc.id)
        if not result:
            raise ConflictWhenUpdate(
                "TOC section should not contain subsections and commands "
            )
        return

    async def get_command(self, command_id: int) -> CommandInDb:
        command = await queries_nms.get_command_by_id(self.connection, command_id)
        if not command:
            raise EntityDoesNotExist(f"Command with id={command_id} does not exists")
        return command

    async def get_command_by_name(self, name: str) -> CommandInDb:
        command = await queries_nms.get_command_by_name(self.connection, name)
        if not command:
            raise EntityDoesNotExist(f"Command with name={name} does not exists")
        return command

    async def create_command(self, command_data: CommandInCreate) -> CommandInDb:
        try:
            command = await queries_nms.create_command(
                self.connection,
                equipment_id=command_data.equipment_id,
                toc_id=command_data.toc_id,
                name=command_data.name,
                name_full=command_data.name_full,
                description=command_data.description,
                undo_cmd_id=command_data.undo_cmd_id,
            )
        except PostgresError as err:
            raise ConflictWhenInsert(
                f"Insert new entity in database raising a unique violation or exclusion constraint violation error: {str(err)}"
            )
        return CommandInDb(**command)

    async def update_command(
        self,
        *,
        command: CommandInDb,
        equipment_id: Optional[int],
        toc_id: Optional[int],
        name: Optional[str],
        name_full: Optional[str],
        description: Optional[str],
        undo_cmd_id: Optional[int],
    ) -> CommandInDb:
        command_update = command.copy(deep=True)
        command_update.equipment_id = equipment_id or command.equipment_id
        command_update.toc_id = toc_id or command.toc_id
        command_update.name = name or command.name
        command_update.name_full = name_full or command.name_full
        command_update.description = description or command.description
        command_update.undo_cmd_id = undo_cmd_id or command.undo_cmd_id

        try:
            async with self.connection.transaction():
                command_update = await queries_nms.update_command(
                    self.connection,
                    command_id=command_update.id,
                    equipment_id=command_update.equipment_id,
                    toc_id=command_update.toc_id,
                    name=command_update.name,
                    name_full=command_update.name_full,
                    description=command_update.description,
                    undo_cmd_id=command_update.undo_cmd_id,
                )
        except PostgresError as err:
            raise ConflictWhenUpdate(
                f"Insert new entity in database raising a unique violation or exclusion constraint violation error: {str(err)}"
            )
        return CommandInDb(**command_update)

    async def delete_command(self, command: CommandInDb):
        result = await queries_nms.delete_command(
            self.connection, command_id=command.id
        )
        if not result:
            raise ConflictWhenUpdate()
        return

    # FIXME: @cached(noself=True) -- нет заметного прироста скорости, даже наооборот
    # async def get_commands_catalog_total(self, queries):
    #     log.debug("Execute non cached query get_commands_catalog_total")
    #     return await queries.get_commands_catalog_total(self.connection)

    async def search_commands_catalog(
        self,
        *,
        limit: int = 1500,
        page: int = 1,
        name: Optional[str] = None,
        toc_id: Optional[int] = None,
        equipment_id: Optional[int] = None,
        equipment_name: Optional[str] = None,
    ) -> ResponsePage[CommandInCatalogResponse]:
        params = dict()
        sql_filters = list()
        if name:
            params["name"] = name
            sql_filters.append(f"lower(c.name) = lower('{name}')")
        if toc_id:
            params["toc-id"] = toc_id
            sql_filters.append(
                f"""c.toc_id in (select t.id from commands_toc t where not t.archive
                   and t.parent_path || t.id::text <@ (select parent_path || id::text from commands_toc
                   where id = {toc_id} and not archive))"""
            )
        if equipment_id:
            params["equipment-id"]: int = equipment_id
            sql_filters.append(f"c.equipment_id = {equipment_id}")
        if equipment_name:
            params["equipment-name"] = equipment_name
            sql_filters.append(f"lower(e.name) = lower('{equipment_name}')")

        offset = (page - 1) * limit
        queries = build_queries_search_commands_catalog(sql_filters)
        total = await queries.get_commands_catalog_total(self.connection)
        commands = await queries.search_commands_catalog(self.connection, limit, offset)

        return ResponsePage(
            page=page, limit=limit, total=total, params=params, content=commands
        )
