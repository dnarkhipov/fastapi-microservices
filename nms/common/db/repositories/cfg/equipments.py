from typing import Optional

from asyncpg import PostgresError

from nms.common.db.errors import (
    ConflictWhenInsert,
    ConflictWhenUpdate,
    EntityDoesNotExist,
)
from nms.common.db.queries.nms import queries_nms
from nms.common.db.repositories.base import BaseNmsRepository
from nms.common.models.equipments import (
    EquipmentInCreate,
    EquipmentInDb,
    EquipmentInResponse,
)

from .utils import build_catalog


class EquipmentsRepository(BaseNmsRepository):
    async def get_equipments_catalog(self, root_item_id: Optional[int] = None) -> list:
        if root_item_id:
            equipments = await queries_nms.get_equipments_from(
                self.connection, root_item_id
            )
        else:
            equipments = await queries_nms.get_equipments_all(self.connection)
        return build_catalog(
            equipments, lambda e: EquipmentInResponse.from_orm(e).dict()
        )

    async def get_equipment(self, equipment_id: int) -> EquipmentInDb:
        equipment = await queries_nms.get_equipment_by_id(self.connection, equipment_id)
        if not equipment:
            raise EntityDoesNotExist(
                f"Equipment with id={equipment_id} does not exists"
            )
        return equipment

    async def get_equipment_by_name(self, name: str) -> EquipmentInDb:
        equipment = await queries_nms.get_equipment_by_name(self.connection, name)
        if not equipment:
            raise EntityDoesNotExist(f"Equipment with name={name} does not exists")
        return equipment

    async def create_equipment(
        self, equipment_data: EquipmentInCreate
    ) -> EquipmentInDb:
        try:
            equipment = await queries_nms.create_equipment(
                self.connection,
                parent_id=equipment_data.parent_id,
                name=equipment_data.name,
                name_full=equipment_data.name_full,
            )
        except PostgresError as err:
            raise ConflictWhenInsert(
                f"Insert new entity in database raising a unique violation or exclusion constraint violation error: {str(err)}"
            )
        return EquipmentInDb(**equipment)

    async def update_equipment(
        self,
        *,
        equipment: EquipmentInDb,
        parent_id: Optional[int],
        name: Optional[str],
        name_full: Optional[str],
    ) -> EquipmentInDb:
        equipment_update = equipment.copy(deep=True)
        equipment_update.parent_id = parent_id
        equipment_update.name = name or equipment.name
        equipment_update.name_full = name_full or equipment.name_full

        try:
            async with self.connection.transaction():
                equipment_update = await queries_nms.update_equipment(
                    self.connection,
                    equipment_id=equipment_update.id,
                    parent_id=equipment_update.parent_id,
                    name=equipment_update.name,
                    name_full=equipment_update.name_full,
                )
        except PostgresError as err:
            raise ConflictWhenUpdate(
                f"Update entity in database raising a unique violation or exclusion constraint violation error: {str(err)}"
            )
        return EquipmentInDb(**equipment_update)

    async def delete_equipment(self, equipment: EquipmentInDb, recursive: bool = False):
        if recursive:
            result = await queries_nms.delete_equipment_recursive(
                self.connection, equipment.id
            )
            if not result:
                raise ConflictWhenUpdate()
        else:
            result = await queries_nms.delete_equipment(self.connection, equipment.id)
            if not result:
                raise ConflictWhenUpdate()
        return
