from fastapi import APIRouter, Request

from nms.common.models.service import AboutInfoResponse, CtrlInfoResponse

router = APIRouter()


@router.get(
    "/",
    name="service:get-about-info",
    summary="информация о версии, разработчиках и т.п.",
    response_model=AboutInfoResponse,
)
def get_about_info(request: Request) -> AboutInfoResponse:
    service = request.app.state.core
    return service.get_about()


@router.get(
    "/ctrl",
    name="service:get-ctrl-info",
    summary="диагностическая информация о сервисе",
    response_model=CtrlInfoResponse,
)
def get_ctrl_info(request: Request) -> CtrlInfoResponse:
    service = request.app.state.core
    return service.get_status()
