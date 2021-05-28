from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class EquipmentBase(BaseModel):
    id: int = Field(description="идентификатор оборудования")
    parent_path: str = Field(description="полный путь до родительского объекта")
    parent_path_name: str = Field(
        description="полный путь до родительского объекта (name)"
    )
    parent_id: Optional[int] = Field(description="ссылка на родительский объект")
    name: str = Field(description="обозначение на схеме")
    name_full: str = Field(description="наименование")


class EquipmentInResponse(EquipmentBase):
    class Config:
        orm_mode = True


class EquipmentInDb(EquipmentBase):
    create_dt: datetime = Field(description="время создания записи")
    update_dt: datetime = Field(description="время последнего обновления записи")


class EquipmentInCreate(BaseModel):
    parent_id: Optional[int] = Field(
        description="ссылка на родительский объект, если отсутствует, то оборудование размещается в корне каталога"
    )
    name: str = Field(min_length=1, max_length=50, description="обозначение на схеме")
    name_full: str = Field(min_length=1, max_length=150, description="наименование")


class EquipmentInUpdate(BaseModel):
    parent_id: Optional[int] = Field(
        description="ссылка на родительский объект, если отсутствует, то оборудование размещается в корне каталога"
    )
    name: Optional[str] = Field(
        min_length=1, max_length=50, description="обозначение на схеме"
    )
    name_full: Optional[str] = Field(
        min_length=1, max_length=150, description="наименование"
    )
