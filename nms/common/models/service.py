from datetime import datetime

from pydantic import BaseModel


class CoreServiceInfo(BaseModel):
    uuid: str
    version: str = "0.0.0"
    about: str = ""
    about_ru: str = ""
    description: str = ""
    copyright: str = ""


class AboutInfoResponse(BaseModel):
    uuid: str
    version: str
    about: str
    about_ru: str
    description: str
    copyright: str

    class Config:
        orm_mode = True


class UptimeResponse(BaseModel):
    days: int
    hours: int
    minutes: int
    seconds: int


class CtrlInfoResponse(BaseModel):
    timestamp: datetime
    uuid: str
    health_code: int
    uptime: UptimeResponse
