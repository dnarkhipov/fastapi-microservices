from fastapi import Depends, HTTPException, Path, status

from nms.common.api.dependencies.database import get_db_repository
from nms.common.db.errors import EntityDoesNotExist
from nms.common.db.repositories.cfg.telemetry import TmRepository
from nms.common.models.telemetry import TmParameterInDb


async def get_tm_parameter_by_id(
    parameter_id: int = Path(..., ge=1),
    repo: TmRepository = Depends(get_db_repository(TmRepository)),
) -> TmParameterInDb:
    try:
        return await repo.get_tm_parameter(parameter_id=parameter_id)
    except EntityDoesNotExist as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
