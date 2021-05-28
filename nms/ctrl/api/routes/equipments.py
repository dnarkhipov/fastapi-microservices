from fastapi import APIRouter, Depends, HTTPException, status, Path

from nms.common.api.dependencies.equipment import get_equipment_by_id
from nms.common.models.equipments import EquipmentInDb, EquipmentInResponse
from nms.ctrl.models.equipments import Equipment


router = APIRouter(tags=["equipments"])


@router.get(
    "/equipments/{equipment_id}",
    name="ctrl:get-equipment-info",
    summary="общий статус оборудования и список параметров, доступных для контроля и изменения",
    response_model=EquipmentInResponse,
)
async def get_equipment(
    equipment: EquipmentInDb = Depends(get_equipment_by_id),
) -> EquipmentInResponse:
    return EquipmentInResponse.from_orm(equipment)


@router.get(
    "/equipments/{equipment_id}/{parameter_id}",
    name="ctrl:get-equipment-parameter",
    summary="значение параметра parameter_id для указанного оборудования",
    response_model=dict,
)
async def get_equipment_parameter(
    parameter_id: str = Path(
        ..., min_length=1, description="Идентификатор параметра заданного оборудования"
    ),
    equipment: EquipmentInDb = Depends(get_equipment_by_id),
) -> dict:
    if parameter_id.lower() in equipment.params:
        return equipment.get_param(parameter_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unsupported parameter id",
        )
