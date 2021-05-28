from fastapi import Depends, HTTPException, Path, status

from nms.common.api.dependencies.database import get_db_repository
from nms.common.db.errors import EntityDoesNotExist
from nms.common.db.repositories.cfg.commands import CommandsRepository
from nms.common.models.commands import CommandInDb, CommandsTocInDb


async def get_command_by_id(
    command_id: int = Path(..., ge=1),
    repo: CommandsRepository = Depends(get_db_repository(CommandsRepository)),
) -> CommandInDb:
    try:
        return await repo.get_command(command_id=command_id)
    except EntityDoesNotExist as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


async def get_commands_toc_by_id(
    toc_id: int = Path(..., ge=1),
    repo: CommandsRepository = Depends(get_db_repository(CommandsRepository)),
) -> CommandsTocInDb:
    try:
        return await repo.get_toc(toc_id)
    except EntityDoesNotExist as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
