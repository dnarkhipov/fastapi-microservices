import logging

from nms.common.api.app import create_application
from nms.common.config import DSNType, get_settings
from nms.common.db.events import connect_to_db

from . import version
from .api.routes import commands, equipments, telemetry

log = logging.getLogger("app")
api_prefix = "/api/v1/cfg"

app = create_application(
    uuid=version.APP_UUID,
    title=version.APP_TITLE,
    description=version.APP_DESCRIPTION,
    version=version.__version__,
    about=version.ABOUT,
    about_ru=version.ABOUT_RU,
    copyright=version.__copyright__,
)

app.include_router(equipments.router, prefix=api_prefix)
app.include_router(commands.router, prefix=api_prefix)
app.include_router(telemetry.router, prefix=api_prefix)


@app.on_event("startup")
async def startup_event():
    log.debug("Starting up...")

    settings = get_settings()
    log.debug(f"Connecting to {settings.db_nms_dsn}")
    pool = await connect_to_db(repr(settings.db_nms_dsn))
    app.state.core.register_connection_pool(DSNType.NMS, pool)
    log.debug("Connection established")


@app.on_event("shutdown")
async def shutdown_event():
    log.debug("Shutting down...")
    log.debug("Closing connections to database")
    await app.state.core.close_all_pools()
    log.debug("Connection closed")
