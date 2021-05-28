from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CommandsTocBase(BaseModel):
    id: int = Field(description="идентификатор раздела")
    parent_path: str = Field(description="полный путь до родительского раздела")
    parent_path_name: str = Field(
        description="полный путь до родительского раздела (name)"
    )
    parent_id: Optional[int] = Field(description="ссылка на родительский раздел")
    name: str = Field(description="название раздела")


class CommandsTocInResponse(CommandsTocBase):
    class Config:
        orm_mode = True


class CommandsTocInCreate(BaseModel):
    parent_id: Optional[int] = Field(
        description="ссылка на родительский раздел, если отсутствует, то раздел создается в корне каталога"
    )
    name: str = Field(min_length=1, max_length=100, description="название раздела")


class CommandsTocInUpdate(BaseModel):
    parent_id: Optional[int] = Field(
        description="ссылка на родительский раздел, если отсутствует, то раздел создается в корне каталога"
    )
    name: Optional[str] = Field(
        min_length=1, max_length=100, description="название раздела"
    )


class CommandsTocInDb(CommandsTocBase):
    create_dt: datetime = Field(description="время создания записи")
    update_dt: datetime = Field(description="время последнего обновления записи")


class CommandBase(BaseModel):
    id: int = Field(description="идентификатор команды")
    equipment_id: int = Field(
        description="ссылка на объект, к которому относится команда"
    )
    toc_id: int = Field(description="тип по каталогу")
    name: str = Field(description="код (номер) команды")
    name_full: str = Field(description="полное наименование команды")
    description: str = Field(description="описание (действие) команды")
    undo_cmd_id: Optional[int] = Field(description="ссылка на команду отмены")


class CommandInResponse(CommandBase):
    class Config:
        orm_mode = True


class CommandInCatalogResponse(CommandInResponse):
    equipment_name: str = Field(description="обозначение объекта на схеме")
    undo_cmd_name: Optional[str] = Field(description="код (номер) команды отмены")


class CommandInCreate(BaseModel):
    equipment_id: int = Field(
        description="ссылка на объект, к которому относится команда"
    )
    toc_id: int = Field(description="тип по каталогу")
    name: str = Field(min_length=1, max_length=10, description="код (номер) команды")
    name_full: str = Field(
        min_length=1, max_length=150, description="полное наименование команды"
    )
    description: str = Field(
        min_length=1, max_length=300, description="описание (действие) команды"
    )
    undo_cmd_id: Optional[int] = Field(description="ссылка на команду отмены")


class CommandInUpdate(BaseModel):
    equipment_id: Optional[int] = Field(
        description="ссылка на объект, к которому относится команда"
    )
    toc_id: Optional[int] = Field(description="тип по каталогу")
    name: Optional[str] = Field(
        min_length=1, max_length=10, description="код (номер) команды"
    )
    name_full: Optional[str] = Field(
        min_length=1, max_length=150, description="полное наименование команды"
    )
    description: Optional[str] = Field(
        min_length=1, max_length=300, description="описание (действие) команды"
    )
    undo_cmd_id: Optional[int] = Field(description="ссылка на команду отмены")


class CommandInDb(CommandBase):
    create_dt: datetime = Field(description="время создания записи")
    update_dt: datetime = Field(description="время последнего обновления записи")
