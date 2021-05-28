from typing import List

from fastapi import APIRouter, Body, Response, status

from nms.common.api.gzip_request import GzipRoute
from nms.common.models.rfspectrumtrace import RfSpectrumSignal
from nms.inbox.models.traces import RfSpectrumTraceInRequest

router = APIRouter(
    prefix='/inbox',
    tags=['inbox'],
    route_class=GzipRoute
)


@router.post(
    '/traces',
    name='inbox:post-trace-data',
    summary='Передать данные о новой спектрограмме',
    status_code=status.HTTP_201_CREATED
)
async def post_trace_data(
        trace_unpacked: RfSpectrumTraceInRequest = Body(...)
):
    trace = trace_unpacked.as_packed_trace()
    return {"guid": trace.guid}


@router.post(
    '/signals',
    name='inbox:post-trace-signals',
    summary='Передать данные массива сигналов спектрограммы',
    status_code=status.HTTP_201_CREATED
)
async def post_trace_signals(
        signals: List[RfSpectrumSignal] = Body(...)
):
    return [signal.guid for signal in signals]
