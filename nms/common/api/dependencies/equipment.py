from fastapi import Depends, HTTPException, Path, status

from nms.common.api.dependencies.database import get_db_repository
from nms.common.db.errors import EntityDoesNotExist
from nms.common.db.repositories.cfg.equipments import EquipmentsRepository
from nms.common.models.equipments import EquipmentInDb


async def get_equipment_by_id(
    equipment_id: int = Path(..., ge=1),
    repo: EquipmentsRepository = Depends(get_db_repository(EquipmentsRepository)),
) -> EquipmentInDb:
    try:
        return await repo.get_equipment(equipment_id=equipment_id)
    except EntityDoesNotExist as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
