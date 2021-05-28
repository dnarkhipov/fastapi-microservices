import logging
from enum import Enum
from functools import lru_cache

from pydantic import AnyUrl, BaseSettings, Field, PostgresDsn, SecretStr

log = logging.getLogger("app")


class DSNType(Enum):
    UNKNOWN = 0
    AUTH = 1
    NMS = 2
    DWH = 3
    ADMIN = 4


class RabbitDsn(AnyUrl):
    allowed_schemes = {"amqp"}
    user_required = True

    def __repr__(self) -> str:
        return f"{self.scheme}://{self.user}:{self.password}@{self.host}{self.path}"

    def __str__(self) -> str:
        return f"{self.scheme}://{self.user}:********@{self.host}{self.path}"


class PostgresDsnV2(PostgresDsn):
    def __repr__(self) -> str:
        return f"{self.scheme}://{self.user}:{self.password}@{self.host}{self.path}"

    def __str__(self) -> str:
        return f"{self.scheme}://{self.user}:********@{self.host}{self.path}"


class Settings(BaseSettings):
    environment: str = "prod"
    testing: bool = False
    debug: bool = False
    api_prefix: str = "/api/v1"
    db_nms_dsn: PostgresDsnV2
    db_dwh_dsn: PostgresDsnV2

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    log.debug("Loading config settings from the environment...")
    return Settings()
