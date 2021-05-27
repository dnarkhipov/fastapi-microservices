# Реализация в одном проекте набора отдельных микросервисов на базе FastAPI

> Это пример организации кода python-модуля, демонстрация концепта решения, "вырванная" из рабочего проекта без гарантий работоспособности "из коробки", дальнейшего развития и поддержки.

## Ключевые особенности

- Проект ориентирован на одновременную работу с отдельными сервисами и общей библиотекой в рамках одного git-репозитория
- В общем случае библиотека устанавливается на каждом сервере в кластере системы, а контекст роли, выполняемой каждой точкой системы, определяется выполняющимся FastAPI-приложением, реализующим отдельный набор API микросервиса
- Отсутвующие в данном примере, но важные компоненты архитектуры решения:
    - Интеграционная шина для обмена сообщениями на базе RabbitMQ
    - Кэширование и обмен данными между экземплярами сервисов на базе Redis
- Весь набор микросервисов и разделяемый код скомпонован в одном Python-модуле, со следующей структурой:
    - `nms` - модуль-обертка для отдельных сервисов и модуля с разделяемым кодом
    - `nms.common` - модуль с разделяемым кодом
    - `nms.auth` - сервис авторизации пользователей и управления пользователями
    - `nms.cfg` - сервис, реализующий управление конфигурацией управляемой системы
    - `nms.inbox` - сервис интеграции с внешней системой (интеграционный API)
    - `nms.{...}` - каждый новый сервис

> Пример: запуск сервиса авторизации пользователей
> ```shell
> # Development server
> uvicorn nms.auth.main:app --host 0.0.0.0 --port 4000 --workers 1  --log-config loggers.json
> 
> # Production server
> gunicorn --bind 0.0.0.0:$PORT --workers=4 nms.auth.main:app -k uvicorn.workers.UvicornWorker
> ```

## Комментарии по реализации
Конфигурация сервиса может быть задана:
- с помощью переменных окружения (в приоритете)
- в локальном .env -файле
```shell
TZ=Europe/Moscow
ENVIRONMENT=dev
TESTING=True
DEBUG=True
DB_NMS_DSN=postgres://nms:nms@nms-db:5432/nms
DB_DWH_DSN=postgres://dwh:dwh@nms-db:5432/dwh
JWT_SECRET_KEY=P4xCg7Dhk+Db
```

Сервисы могут работать одновременно с разными БД, доступ к которым определяется базовым типом используемого репозитория
```python
# типы репозиториев БД
class BaseNmsRepository(BaseRepository):
    _dsn_type = DSNType.NMS


class BaseAuthRepository(BaseRepository):
    _dsn_type = DSNType.AUTH


class BaseDwhRepository(BaseRepository):
    _dsn_type = DSNType.DWH


class BaseAdminRepository(BaseRepository):
    _dsn_type = DSNType.ADMIN

```


### Инициализация окружения с помощью [Poetry](https://python-poetry.org/docs/)

```shell
poetry install
```

### Развертывание в Docker. Подготовка и инициализация БД

1. Необходимо предварительно создать docker volume:
```shell
docker volume create nms-db-data
```
2. Выполнить первый запуск БД. При первом старте БД (пустом разделе nms-db-data) будет выполнен скрипт `db/create-db-v3.sh` , создающий необходимые базы.
```shell
docker-compose up -d nms-db
```
3. После успешного старта БД и инициализации необходимо применить миграции для всех баз. В качестве инструмента миграции для БД в данном проекте используется пакет [aiosqlembic](https://pypi.org/project/aiosqlembic/):
```shell
cd ./db
aiosqlembic -m ./auth/migrations asyncpg postgres://auth:auth@localhost:5432/auth up
aiosqlembic -m ./nms/migrations asyncpg postgres://nms:nms@localhost:5432/nms up
...
```
