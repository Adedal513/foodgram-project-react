# Продуктовый помощник Foodgram
![workflow results](https://github.com/Adedal513/foodgram-project-react/actions/workflows/main.yml/badge.svg)
## Описание

Foodgram -- онлайн-сервис продуктового помощника. На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Установка
Клонируйте репозиторий и перейлите в корневой каталог:

```bash
git clone git@github.com:Adedal513/foodgram-project-react.git
cd foodgram-roject-react
```
### Локальный запуск
---
Для работы сервису необходимы переменные окружения:

- ALLOWED_HOSTS
- INTERNAL_IPS
- SECRET_KEY
- DEBUG
- DB_ENGINE
- POSTGRES_HOST
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_PORT

Запуск сервиса происходит при помощи `docker-compose`. В корневой директории проекта произведите запуск сервиса (в ходе выполнения команды могут потребоваться root-права):
```
docker-compose up -d
```
К моменту запуска, сервис соберет статику и выполнит необходимые миграции. В случае необходимости, логи Django и Gunicorn можно найти в папке `infra/gunicorn_log/`.

Для заполнения БД дефолтными данными, выполните команду
```
docker-compose exec app python manage.py load_db
```
Cервис станет доступен по адресу:

http://localhost:8000

Документация:

http://localhost:8000/api/docs

### Запуск на удаленном сервере
---
Клонируйте репозиторий и перейлите в корневой каталог:

```bash
git clone git@github.com:Adedal513/foodgram-project-react.git
cd foodgram-roject-react
```

Отредактируйте файл `infra/nginx.conf`, указав необходимый IP адрес вашего сервера в строке `server_name`.
 
Установите соединение с сервером и последовательно скопируйте все необходимые директории:
```
sudo scp -r data/ user@ip_address:/
sudo scp -r infra/ user@ip_address:/
sudo scp -r init_db/ user@ip_address:/
```
Убедитесь, что на удаленном сервере утсановлены [Docker](https://docs.docker.com/engine/install/) и [Docker-compose](https://github.com/docker/compose#where-to-get-docker-compose).
Подключитесь к удаленному серверу и создайте в директории `infra` файл с переменными окружения `.env` (см. Локальный запуск).

Запуск сервиса происходит при помощи `docker-compose`. В корневой директории проекта произведите запуск сервиса (в ходе выполнения команды могут потребоваться root-права):
```
docker-compose up -d
```
К моменту запуска, сервис соберет статику и выполнит необходимые миграции. В случае необходимости, логи Django и Gunicorn можно найти в папке `infra/gunicorn_log/`.

Для заполнения БД дефолтными данными, выполните команду
```
docker-compose exec app python manage.py load_db
```

# Ссылки

Пример развернутого проекта: http://84.252.139.46