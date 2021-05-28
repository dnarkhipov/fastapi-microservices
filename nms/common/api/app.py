from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from nms.common.api.errors import http422_error_handler, http_error_handler
from nms.common.config import get_settings
from nms.common.service import CoreServiceInfo, get_service

from .routes import service


def create_application(uuid: str, **kwargs) -> FastAPI:
    settings = get_settings()
    if settings.environment == "dev":
        docs_kwargs = dict()
    else:
        docs_kwargs = dict(docs_url=None, redoc_url=None)

    app = FastAPI(
        title=kwargs.get("title", "Generic API service"),
        description=kwargs.get("description", ""),
        version=kwargs.get("version", "0.1.0"),
        debug=get_settings().debug,
        **docs_kwargs
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # TODO Добавить ограничение на кол-во запросов в секунду (fastapi rate limit)!

    # TODO При наличии в запросе заголовка Accept-Encoding: gzip , сжимаем все, что более 50КБ
    app.add_middleware(GZipMiddleware, minimum_size=50 * 1024)

    app.add_exception_handler(HTTPException, http_error_handler)
    app.add_exception_handler(RequestValidationError, http422_error_handler)

    app.include_router(service.router)

    core_service_info = CoreServiceInfo(uuid=uuid, **kwargs)
    app.state.core = get_service(core_service_info)

    return app
