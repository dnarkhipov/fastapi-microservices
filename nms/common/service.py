from datetime import datetime, timedelta

from nms.common.config import DSNType
from nms.common.models.service import (
    AboutInfoResponse,
    CoreServiceInfo,
    CtrlInfoResponse,
    UptimeResponse,
)


class CoreService:
    """Хранит общие данные сервиса определенного типа, независимо от количества экземпляров этого сервиса."""

    __instance = None

    def __init__(self, info: CoreServiceInfo):
        self.uuid = info.uuid
        self.version = info.version
        self.about = info.about
        self.about_ru = info.about_ru
        self.copyright = info.copyright
        self.description = info.description
        # TODO Чтение параметров сервиса из общего для потоков кэша (redis)
        self._startup_time = datetime.now().astimezone()

        self._connection_pool = dict()

    @staticmethod
    def get_instance(service_info: CoreServiceInfo = None):
        if not CoreService.__instance:
            if not service_info:
                raise ValueError("Call __init__ with service_info == None")
            CoreService.__instance = CoreService(service_info)
        return CoreService.__instance

    def get_about(self) -> AboutInfoResponse:
        return AboutInfoResponse.from_orm(self)

    @property
    def uptime(self) -> UptimeResponse:
        def _uptime() -> timedelta:
            return datetime.now().astimezone() - self._startup_time

        days, remainder = divmod(_uptime().total_seconds(), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        return UptimeResponse(
            days=int(days), hours=int(hours), minutes=int(minutes), seconds=int(seconds)
        )

    def get_status(self) -> CtrlInfoResponse:
        return CtrlInfoResponse(
            timestamp=datetime.now().astimezone(),
            uuid=self.uuid,
            # TODO Возврат кода текущего состояния сервиса
            # Код статуса сервиса - код, отражающий текущие проблемы в работе сервиса
            # 0 - проблем в работе сервиса нет
            health_code=0,
            uptime=self.uptime,
        )

    def register_connection_pool(self, dsn_type: DSNType, pool):
        self._connection_pool[dsn_type] = pool

    async def close_all_pools(self):
        for dsn_type, pool in self._connection_pool.items():
            if dsn_type in (DSNType.NMS, DSNType.ADMIN, DSNType.AUTH, DSNType.DWH):
                await pool.close()
            else:
                raise ValueError(f"The requested DSN Type is not supported: {dsn_type}")

    def get_connection_pool(self, dsn_type: DSNType):
        pool = self._connection_pool.get(dsn_type)
        if not pool:
            raise ValueError(f"The requested DSN Type is not supported: {dsn_type}")
        return pool


def get_service(service_info: CoreServiceInfo = None) -> CoreService:
    return CoreService.get_instance(service_info)
