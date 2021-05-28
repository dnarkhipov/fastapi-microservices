from typing import Optional

from asyncpg import PostgresError

from nms.common.db.errors import (
    ConflictWhenInsert,
    ConflictWhenUpdate,
    EntityDoesNotExist,
)
from nms.common.db.queries.nms import (
    build_queries_search_telemetry_catalog,
    queries_nms,
)
from nms.common.db.repositories.base import BaseNmsRepository
from nms.common.models.telemetry import (
    TmParameterInCreate,
    TmParameterInDb,
    TmParameterInResponse,
)
from nms.common.models.response_pagination import ResponsePage


class TmRepository(BaseNmsRepository):
    async def search_telemetry_catalog(
        self,
        *,
        limit: int = 100,
        page: int = 1,
        name: Optional[str] = None,
    ) -> ResponsePage[TmParameterInResponse]:
        params = dict()
        sql_filters = list()
        if name:
            params["name"] = name
            sql_filters.append(f"lower(name) = lower('{name}')")

        offset = (page - 1) * limit
        queries = build_queries_search_telemetry_catalog(sql_filters)
        total = await queries.get_telemetry_catalog_total(self.connection)
        tm_params = await queries.search_telemetry_catalog(
            self.connection, limit, offset
        )

        return ResponsePage(
            page=page, limit=limit, total=total, params=params, content=tm_params
        )

    async def get_tm_parameter(self, parameter_id: int) -> TmParameterInDb:
        parameter = await queries_nms.get_tm_parameter_by_id(
            self.connection, parameter_id
        )
        if not parameter:
            raise EntityDoesNotExist(
                f"Telemetry parameter with id={parameter_id} does not exists"
            )
        return parameter

    async def get_tm_parameter_by_name(self, name: str) -> TmParameterInDb:
        command = await queries_nms.get_tm_parameter_by_name(self.connection, name)
        if not command:
            raise EntityDoesNotExist(f"Command with name={name} does not exists")
        return command

    async def create_tm_parameter(
        self, parameter_data: TmParameterInCreate
    ) -> TmParameterInDb:
        try:
            parameter = await queries_nms.create_tm_parameter(
                self.connection,
                name=parameter_data.name,
                name_full=parameter_data.name_full,
                description=parameter_data.description,
                value_validator=parameter_data.value_validator,
            )
        except PostgresError as err:
            raise ConflictWhenInsert(
                f"Insert new entity in database raising a unique violation or exclusion constraint violation error: {str(err)}"
            )
        return TmParameterInDb(**parameter)

    async def update_tm_parameter(
        self,
        *,
        tm_parameter: TmParameterInDb,
        name: Optional[str],
        name_full: Optional[str],
        description: Optional[str],
        value_validator: Optional[dict],
    ) -> TmParameterInDb:
        parameter_update = tm_parameter.copy(deep=True)
        parameter_update.name = name or tm_parameter.name
        parameter_update.name_full = name_full or tm_parameter.name_full
        parameter_update.description = description or tm_parameter.description
        parameter_update.value_validator = (
            value_validator or tm_parameter.value_validator
        )

        try:
            async with self.connection.transaction():
                parameter_update = await queries_nms.update_tm_parameter(
                    self.connection,
                    parameter_id=parameter_update.id,
                    name=parameter_update.name,
                    name_full=parameter_update.name_full,
                    description=parameter_update.description,
                    value_validator=parameter_update.value_validator,
                )
        except PostgresError as err:
            raise ConflictWhenUpdate(
                f"Insert new entity in database raising a unique violation or exclusion constraint violation error: {str(err)}"
            )
        return TmParameterInDb(**parameter_update)

    async def delete_tm_parameter(self, parameter: TmParameterInDb):
        result = await queries_nms.delete_tm_parameter(
            self.connection, parameter_id=parameter.id
        )
        if not result:
            raise ConflictWhenUpdate()
        return
