from typing import Any, List, Optional

from fastapi import (APIRouter, Body, Depends, HTTPException, Query, Response,
                     status)

from nms.common.api.dependencies.command import (get_command_by_id,
                                                 get_commands_toc_by_id)
from nms.common.api.dependencies.database import get_db_repository
from nms.common.db.errors import (ConflictWhenInsert, ConflictWhenUpdate)
from nms.common.db.repositories.cfg.commands import CommandsRepository
from nms.common.models.commands import (CommandInCatalogResponse,
                                        CommandInCreate, CommandInDb,
                                        CommandInResponse, CommandInUpdate,
                                        CommandsTocInCreate, CommandsTocInDb,
                                        CommandsTocInResponse,
                                        CommandsTocInUpdate)
from nms.common.models.response_pagination import ResponsePage

router = APIRouter(tags=["commands"])


@router.get(
    "/commands-toc",
    name="cfg:get-commands-toc-catalog",
    summary="структура каталога команд управления",
    response_model=list,
)
async def get_commands_toc_catalog(
    repo: CommandsRepository = Depends(get_db_repository(CommandsRepository)),
):
    return await repo.get_toc_catalog()


@router.get(
    "/commands-toc/{toc_id}",
    name="cfg:get-commands-toc",
    summary="поиск раздела каталога по id",
    response_model=CommandsTocInResponse,
)
async def get_commands_toc(
    toc: CommandsTocInDb = Depends(get_commands_toc_by_id),
) -> CommandsTocInResponse:
    return CommandsTocInResponse.from_orm(toc)


@router.post(
    "/commands-toc/",
    name="cfg:create-commands-toc",
    summary="добавить новый раздел в каталог",
    response_model=CommandsTocInResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_commands_toc(
    toc_data: CommandsTocInCreate = Body(...),
    repo: CommandsRepository = Depends(get_db_repository(CommandsRepository)),
) -> CommandsTocInResponse:
    try:
        toc = await repo.create_toc(toc_data)
    except ConflictWhenInsert as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))
    return CommandsTocInResponse.from_orm(toc)


@router.patch(
    "/commands-toc/{toc_id}",
    name="cfg:update-commands-toc",
    summary="изменить атрибуты раздела",
    response_model=CommandsTocInResponse,
)
async def update_commands_toc(
    toc_data: CommandsTocInUpdate = Body(...),
    repo: CommandsRepository = Depends(get_db_repository(CommandsRepository)),
    toc: CommandsTocInDb = Depends(get_commands_toc_by_id),
) -> CommandsTocInResponse:
    try:
        toc_update = await repo.update_toc(toc=toc, **toc_data.dict())
    except ConflictWhenUpdate as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))
    return CommandsTocInResponse.from_orm(toc_update)


@router.delete(
    "/commands-toc/{toc_id}",
    name="cfg:delete-commands-toc",
    summary="удалить раздел каталога (раздел не должен содержать подразделы и команды управления)",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_commands_toc(
    repo: CommandsRepository = Depends(get_db_repository(CommandsRepository)),
    toc: CommandsTocInDb = Depends(get_commands_toc_by_id),
):
    try:
        await repo.delete_toc(toc)
    except ConflictWhenUpdate as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/commands",
    name="cfg:search-commands-catalog",
    summary="поиск в каталоге команд управления и вывод результатов постранично (к фильтрам применяется оператор AND)",
    response_model=ResponsePage[CommandInCatalogResponse],
)
async def search_commands_catalog(
    limit: int = Query(
        default=1500, ge=500, le=5000, description="количество записей на странице"
    ),
    page: int = Query(default=1, gе=1, description="номер страницы"),
    name: Optional[str] = Query(
        None,
        min_length=1,
        max_length=10,
        description="фильтр: код (номер) команды (регистронезависимо)",
    ),
    toc_id: Optional[int] = Query(
        None,
        alias="toc-id",
        description="фильтр: только для раздела и подразделов, начиная с toc_id",
    ),
    equipment_id: Optional[int] = Query(
        None, alias="equipment-id", description="фильтр: по идентификатору оборудования"
    ),
    equipment_name: Optional[str] = Query(
        None,
        alias="equipment-name",
        min_length=1,
        max_length=50,
        description="фильтр: по оборудованию, обозначение на схеме (регистронезависимо)",
    ),
    repo: CommandsRepository = Depends(get_db_repository(CommandsRepository)),
) -> ResponsePage[CommandInCatalogResponse]:
    return await repo.search_commands_catalog(
        limit=limit,
        page=page,
        name=name,
        toc_id=toc_id,
        equipment_id=equipment_id,
        equipment_name=equipment_name,
    )


@router.get(
    "/commands/{command_id}",
    name="cfg:get-command",
    summary="поиск команды по id",
    response_model=CommandInResponse,
)
async def get_command(
    command: CommandInDb = Depends(get_command_by_id),
) -> CommandInResponse:
    return CommandInResponse.from_orm(command)


@router.post(
    "/commands/",
    name="cfg:create-command",
    summary="добавить новую команду",
    response_model=CommandInResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_command(
    command_data: CommandInCreate = Body(...),
    repo: CommandsRepository = Depends(get_db_repository(CommandsRepository)),
) -> CommandInResponse:
    try:
        command = await repo.create_command(command_data)
    except ConflictWhenInsert as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))
    return CommandInResponse.from_orm(command)


@router.patch(
    "/commands/{command_id}",
    name="cfg:update-command",
    summary="изменить атрибуты команды",
    response_model=CommandInResponse,
)
async def update_command(
    command_data: CommandInUpdate = Body(...),
    repo: CommandsRepository = Depends(get_db_repository(CommandsRepository)),
    command: CommandInDb = Depends(get_command_by_id),
) -> CommandInResponse:
    try:
        command_update = await repo.update_command(
            command=command, **command_data.dict()
        )
    except ConflictWhenUpdate as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))
    return CommandInResponse.from_orm(command_update)


@router.delete(
    "/commands/{command_id}",
    name="cfg:delete-command",
    summary="удалить команду",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_command(
    repo: CommandsRepository = Depends(get_db_repository(CommandsRepository)),
    command: CommandInDb = Depends(get_command_by_id),
):
    try:
        await repo.delete_command(command)
    except ConflictWhenUpdate as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
