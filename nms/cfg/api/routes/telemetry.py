from typing import Optional

from fastapi import (APIRouter, Body, Depends, HTTPException, Query, Response,
                     status)

from nms.common.api.dependencies.database import get_db_repository
from nms.common.api.dependencies.telemetry import get_tm_parameter_by_id
from nms.common.db.errors import (ConflictWhenInsert, ConflictWhenUpdate,
                                  EntityDoesNotExist)
from nms.common.db.repositories.cfg.telemetry import TmRepository
from nms.common.models.telemetry import (TmParameterInCreate, TmParameterInDb,
                                         TmParameterInResponse,
                                         TmParameterInUpdate)
from nms.common.models.response_pagination import ResponsePage


router = APIRouter(tags=["telemetry"])


@router.get(
    "/telemetry",
    name="cfg:search-telemetry-catalog",
    summary="поиск в каталоге ТМ-параметров и вывод результатов постранично (к фильтрам применяется оператор AND)",
    response_model=ResponsePage[TmParameterInResponse],
)
async def search_telemetry_catalog(
    limit: int = Query(
        default=100, ge=50, le=5000, description="количество записей на странице"
    ),
    page: int = Query(default=1, gе=1, description="номер страницы"),
    name: Optional[str] = Query(
        None,
        min_length=1,
        max_length=80,
        description="фильтр: обозначение ТМ-параметра (индекс)",
    ),
    repo: TmRepository = Depends(get_db_repository(TmRepository)),
) -> ResponsePage[TmParameterInResponse]:
    return await repo.search_telemetry_catalog(
        limit=limit,
        page=page,
        name=name
    )


@router.get(
    "/telemetry/{parameter_id}",
    name="cfg:get-tm-parameter",
    summary="поиск ТМ-параметра по id",
    response_model=TmParameterInResponse,
)
async def get_tm_parameter(
    tm_parameter: TmParameterInDb = Depends(get_tm_parameter_by_id),
) -> TmParameterInResponse:
    return TmParameterInResponse.from_orm(tm_parameter)


@router.post(
    "/telemetry/",
    name="cfg:create-tm-parameter",
    summary="добавить новый параметр",
    response_model=TmParameterInResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tm_parameter(
    tm_parameter_data: TmParameterInCreate = Body(...),
    repo: TmRepository = Depends(get_db_repository(TmRepository)),
) -> TmParameterInResponse:
    try:
        parameter = await repo.create_tm_parameter(parameter_data=tm_parameter_data)
    except ConflictWhenInsert as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))
    return TmParameterInResponse.from_orm(parameter)


@router.patch(
    "/telemetry/{parameter_id}",
    name="cfg:update-tm-parameter",
    summary="изменить атрибуты параметра",
    response_model=TmParameterInResponse,
)
async def update_tm_parameter(
    tm_parameter_data: TmParameterInUpdate = Body(...),
    repo: TmRepository = Depends(get_db_repository(TmRepository)),
    tm_parameter: TmParameterInDb = Depends(get_tm_parameter_by_id),
) -> TmParameterInResponse:
    try:
        parameter_update = await repo.update_tm_parameter(
            tm_parameter=tm_parameter, **tm_parameter_data.dict()
        )
    except ConflictWhenUpdate as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))
    return TmParameterInResponse.from_orm(parameter_update)


@router.delete(
    "/telemetry/{parameter_id}",
    name="cfg:delete-tm-parameter",
    summary="удалить параметр",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_tm_parameter(
    repo: TmRepository = Depends(get_db_repository(TmRepository)),
    tm_parameter: TmParameterInDb = Depends(get_tm_parameter_by_id),
):
    try:
        await repo.delete_tm_parameter(tm_parameter)
    except ConflictWhenUpdate as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
