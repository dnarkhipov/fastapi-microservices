from pathlib import Path

import aiosql

from nms.common.models.commands import (
    CommandInCatalogResponse,
    CommandInDb,
    CommandsTocInDb,
)
from nms.common.models.equipments import EquipmentInDb
from nms.common.models.telemetry import TmParameterInDb, TmParameterInResponse

queries_nms = aiosql.from_path(
    sql_path=Path(__file__).parent / "nms",
    driver_adapter="asyncpg",
    record_classes={
        "EquipmentInDb": EquipmentInDb,
        "CommandInDb": CommandInDb,
        "CommandsTocInDb": CommandsTocInDb,
        "CommandInCatalogResponse": CommandInCatalogResponse,
        "TmParameterInDb": TmParameterInDb,
        "TmParameterInResponse": TmParameterInResponse,
    },
)


def build_queries_search_commands_catalog(filters: list[str]):
    sql_header_search = """
    -- name: search_commands_catalog
    -- record_class: CommandInCatalogResponse
    select c.id,
           c.equipment_id,
           e.name as equipment_name,
           c.toc_id,
           c.name,
           c.name_full,
           c.description,
           c.undo_cmd_id,
           u.name as undo_cmd_name"""

    sql_header_total = """
    -- name: get_commands_catalog_total$
    select count(c.id) as total"""

    sql_text = """
    from commands c
             left join commands u on c.undo_cmd_id = u.id and not u.archive,
         equipment e
    where not c.archive and c.equipment_id = e.id and not e.archive
    """
    for _ in filters:
        sql_text = f"{sql_text} and {_}"

    sql_text = f"""{sql_header_search}{sql_text} order by c.name limit :limit offset :offset;
    {sql_header_total}{sql_text};"""

    return aiosql.from_str(
        sql=sql_text,
        driver_adapter="asyncpg",
        record_classes={"CommandInCatalogResponse": CommandInCatalogResponse},
    )


def build_queries_search_telemetry_catalog(filters: list[str]):
    sql_header_search = """
    -- name: search_telemetry_catalog
    -- record_class: TmParameterInResponse
    select id,
       name,
       name_full,
       description,
       value_validator"""

    sql_header_total = """
    -- name: get_telemetry_catalog_total$
    select count(id) as total"""

    sql_text = """
    from telemetry where not archive"""
    for _ in filters:
        sql_text = f"{sql_text} and {_}"

    sql_text = f"""{sql_header_search}{sql_text} order by name limit :limit offset :offset;
    {sql_header_total}{sql_text};"""

    return aiosql.from_str(
        sql=sql_text,
        driver_adapter="asyncpg",
        record_classes={"TmParameterInResponse": TmParameterInResponse},
    )
