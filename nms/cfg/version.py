from uuid import UUID

__version__ = "0.1.0"
__copyright__ = "Copyright 2021"

APP_TITLE = "Initial Configuration Service"
APP_TITLE_RU = "Сервис управления конфигурацией ИД"
APP_DESCRIPTION = (
    "Управление каталогами ИД (оборудование, команды управления, ТМИ и т.п.)"
)

ABOUT = f"{APP_TITLE} v.{__version__}"
ABOUT_RU = f"{APP_TITLE_RU}. Версия {__version__}"

APP_UUID = UUID("741b029a-d3bd-4a07-b45c-2f7dbcdf531d").hex
