# Реализация в одном проекте набора отдельных микросервисов на базе FastAPI

> Это пример организации кода python-модуля, демонстрация концепта решения, "вырванная" из рабочего проекта без гарантий работоспособности "из коробки", дальнейшего развития и поддержки.

## Ключевые особенности

- Проект ориентирован на одновременную работу с отдельными сервисами и общей библиотекой в рамках одного git-репозитория
- В общем случае библиотека устанавливается на каждом сервере в кластере системы, а контекст роли, выполняемой каждой точкой системы, определяется выполняющимся FastAPI-приложением, реализующим отдельный набор API микросервиса
- Отсутвующие в данном примере, но важные компоненты архитектуры решения:
    - Интеграционная шина для обмена сообщениями на базе RabbitMQ
    - Кэширование и обмен данными между экземплярами сервисов на базе Redis
- Весь набор микросервисов и разделяемый код скомпонован в одном Python-модуле, со следующей структурой:
    - _nms_ - модуль-обертка для отдельных сервисов и модуля с разделяемым кодом
    - _nms.common_ - модуль с разделяемым кодом
    - _nms.auth_ - сервис авторизации пользователей и управления пользователями
    - _nms.cfg_ - сервис, реализующий управление конфигурацией управляемой системы
    - _nms.inbox_ - сервис интеграции с внешней системой (интеграционный API)
    - _nms._{...} - каждый новый сервис

Пример запуска сервиса авторизации пользователей:
```shell
# Development server
uvicorn nms.auth.main:app --host 0.0.0.0 --port 4000 --workers 1  --log-config loggers.json

# Production server
gunicorn --bind 0.0.0.0:$PORT --workers=4 nms.auth.main:app -k uvicorn.workers.UvicornWorker
```



## Развертывание в Docker
### Инициализация БД

Необходимо предварительно создать следующие docker volume:
```shell
docker volume create nms-db-data
```

## TODO
- [traefik proxy](https://doc.traefik.io/traefik/)

