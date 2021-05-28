from typing import Optional

from fastapi import (APIRouter, Body, Depends, HTTPException, Query, Response,
                     status)

from nms.common.api.dependencies.database import get_db_repository
from nms.common.api.dependencies.equipment import get_equipment_by_id
from nms.common.db.errors import (ConflictWhenInsert, ConflictWhenUpdate,
                                  EntityDoesNotExist)
from nms.common.db.repositories.cfg.equipments import EquipmentsRepository
from nms.common.models.equipments import (EquipmentInCreate, EquipmentInDb,
                                          EquipmentInResponse,
                                          EquipmentInUpdate)

router = APIRouter(tags=["equipments"])


@router.get(
    "/equipments",
    name="cfg:search-equipments-catalog",
    summary="поиск оборудования, запрос без параметров возвращает полную структуру управляемой системы",
    response_model=list,
)
async def search_equipments_catalog(
    equipment_id: Optional[int] = Query(
        None, alias="id", description="идентификатор оборудования"
    ),
    name: Optional[str] = Query(
        None,
        min_length=1,
        max_length=50,
        description="обозначение на схеме (регистронезависимо)",
    ),
    root_id: Optional[int] = Query(
        None,
        alias="root-id",
        description="формировать каталог с объекта: идентификатор",
    ),
    root_name: Optional[str] = Query(
        None,
        min_length=1,
        max_length=50,
        alias="root-name",
        description="формировать каталог с объекта: обозначение (регистронезависимо)",
    ),
    repo: EquipmentsRepository = Depends(get_db_repository(EquipmentsRepository)),
) -> list:
    try:
        if equipment_id:
            equipment = await repo.get_equipment(equipment_id)
            return [EquipmentInResponse.from_orm(equipment)]
        elif name:
            equipment = await repo.get_equipment_by_name(name)
            return [EquipmentInResponse.from_orm(equipment)]
        elif root_id:
            return await repo.get_equipments_catalog(root_id)
        elif root_name:
            parent = await repo.get_equipment_by_name(root_name)
            return await repo.get_equipments_catalog(parent.id)
    except EntityDoesNotExist:
        return list()
    return await repo.get_equipments_catalog()


@router.get(
    "/equipments/{equipment_id}",
    name="cfg:get-equipment",
    summary="поиск оборудования по id",
    response_model=EquipmentInResponse,
)
async def get_equipment(
    equipment: EquipmentInDb = Depends(get_equipment_by_id),
) -> EquipmentInResponse:
    return EquipmentInResponse.from_orm(equipment)


@router.post(
    "/equipments/",
    name="cfg:create-equipment",
    summary="добавить новое оборудование",
    response_model=EquipmentInResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_equipment(
    equipment_data: EquipmentInCreate = Body(...),
    repo: EquipmentsRepository = Depends(get_db_repository(EquipmentsRepository)),
) -> EquipmentInResponse:
    try:
        equipment = await repo.create_equipment(equipment_data)
    except ConflictWhenInsert as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))
    return EquipmentInResponse.from_orm(equipment)


@router.patch(
    "/equipments/{equipment_id}",
    name="cfg:update-equipment",
    summary="изменить свойства оборудования",
    response_model=EquipmentInResponse,
)
async def update_equipment(
    equipment_data: EquipmentInUpdate = Body(...),
    repo: EquipmentsRepository = Depends(get_db_repository(EquipmentsRepository)),
    equipment: EquipmentInDb = Depends(get_equipment_by_id),
) -> EquipmentInResponse:
    try:
        equipment_update = await repo.update_equipment(
            equipment=equipment, **equipment_data.dict()
        )
    except ConflictWhenUpdate as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))
    return EquipmentInResponse.from_orm(equipment_update)


@router.delete(
    "/equipments/{equipment_id}",
    name="cfg:delete-equipment",
    summary="удалить оборудование (фактически выполняется архивация)",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_equipment(
    recursive: bool = Query(
        default=False, description="удалить, включая все вложенное оборудование"
    ),
    repo: EquipmentsRepository = Depends(get_db_repository(EquipmentsRepository)),
    equipment: EquipmentInDb = Depends(get_equipment_by_id),
):
    try:
        await repo.delete_equipment(equipment, recursive=recursive)
    except ConflictWhenUpdate as err:
        if recursive:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Try with query option `recursive=true`",
            )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
