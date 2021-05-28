from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TmParameterBase(BaseModel):
    id: int = Field(description="идентификатор ТМ-параметра")
    name: str = Field(description="обозначение (индекс)")
    name_full: str = Field(description="наименование")
    description: str = Field(description="описание")
    value_validator: dict = Field(
        default=dict(), description="формат значения параметра (JSON Schema)"
    )


class TmParameterInResponse(TmParameterBase):
    class Config:
        orm_mode = True


class TmParameterInCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50, description="обозначение (индекс)")
    name_full: str = Field(min_length=1, max_length=200, description="наименование")
    description: str = Field(min_length=1, max_length=300, description="описание")
    value_validator: dict = Field(
        default=dict(), description="формат значения параметра (JSON Schema)"
    )


class TmParameterInUpdate(BaseModel):
    name: Optional[str] = Field(
        min_length=1, max_length=50, description="обозначение (индекс)"
    )
    name_full: Optional[str] = Field(
        min_length=1, max_length=200, description="наименование"
    )
    description: Optional[str] = Field(
        min_length=1, max_length=300, description="описание"
    )
    value_validator: Optional[dict] = Field(
        default=dict(), description="формат значения параметра (JSON Schema)"
    )


class TmParameterInDb(TmParameterBase):
    create_dt: datetime = Field(description="время создания записи")
    update_dt: datetime = Field(description="время последнего обновления записи")
