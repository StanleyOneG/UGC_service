#  **Ссылка на репозиторий** https://github.com/StanleyOneG/ugc_sprint_1


#  **Ссылка на репозиторий Async_API** https://github.com/VladIs10ve/Async_API_sprint_1_team

#  **Ссылка на репозиторий Auth_API** https://github.com/VladIs10ve/Auth_sprint_1

Для интеграции сервисов используется jwt token и общий public_key

#  **Описание**

Это API реализует сохранение и получение прогресса просмотра фильма пользователей, а также управление пользовательским контентом по фильмам.

### Исследование по выбору хранилища описано в директории `research`

#  **Зависимости**

Перед запуском проекта на локальной машине, необходимо установить следующие зависимости:

- Docker
- docker-compose

Для локального запуска:

- Python (версии 3.10)
- библиотеки Python, указанные в файле requirements.txt, можно установить с помощью команды:
  pip install -r requirements.txt

#  **Переменные окружения**

Для запуска приложения необходимо:
- в папку **ugc_api** создать `.env` файл и заполнить его следующими переменными (
значения по умолчанию оставить неизменными):

```
# Параметры хранилище KAFKA
KAFKA_HOST=broker
KAFKA_PORT=9092
KAFKA_TOPIC=topic_ugc

# Параметры базы данных REDIS
REDIS_HOST=redis_ugc
REDIS_PORT=6379

# Общие параметры сервиса
PROJECT_NAME="UGC"
PROJECT_DESCRIPTION="API для записи прогресса просмотра контента"
PROJECT_VERSION="1.0.0"
PROJECT_CACHE_SERVICE_NAME="redis"

STORAGE_DATABASE_NAME=ugc
STORAGE_COLLECTION_NAME=ugc_collection

APP_HOST=0.0.0.0
APP_PORT=8000

# Пример ключа
JWT_PUBLIC_KEY='-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAlrTcXRCF4zF2aWJUfDIR
bpG3C87XRgt/yIVvLNf8ECMULc/owjxfQhc7d1GDa9Gab+T1CUkt6NNX6QW0Nu+c
DboNkHS4f5QSRXoRpk/J/8VQpOOl1KCKeiYYN9KHwu/Vx4l5ffoipHXZqd8pZi6d
2eYqQJvvZ6un/1dEfcdvG0rTIc8M+7eLl+xwzhK5RWG5XT9JErlr4+EHzZML1n3P
s9rBZQZWdc7SsrOzARYGcF5o+mVZcSIusLnWZCyPF9nhdAa0YKu+A+ZxMcKRuO1U
ESKhtRSY3xfoLMmFXz0/okh7w+DO0KumOXpoFoXUV9p3b7+Itt/2VaHYW/sz9CBw
fQIDAQAB
-----END PUBLIC KEY-----'

```

#  **Запуск приложения**

Чтобы запустить приложение локально:

1. Скачайте репозиторий с проектом

    `git clone https://github.com/StanleyOneG/ugc_sprint_1.git`

2. Скачайте репозиторий с Auth сервисом

    `git clone https://github.com/VladIs10ve/Auth_sprint_1.git`

3. Перейдите в директорию с UGC сервисом

    `cd ugc_sprint_1/`

4. Выполните команду

    `make service_up`

    для Linux

    `sudo make service_up`


    Для остановки проекта используйте команду

    `make service_stop`

    для Linux

    `sudo make service_stop`


#  **API**

**Документация в формате OpenAPI:**

Документация Auth API доступна по адресу http://localhost:88/apidocs

Документация UGC API доступна по адресу http://localhost:89/api/openapi/

#  **Как начать**

Для взаимодействия с UGC API необходимо в auth API:

1. Выполнить login под админом (email: admin@admin.com; password: admin)

2. Создать permissions: "subscriber" и "frontend"

3. Выдать данные permissions админу

4. При необходимости обновить access токен с помощью функции Refresh access token в сервисе Auth

Токены хранятся в cookies браузера

***Реализованный функционал***

API предоставляет набор функций для работы с сохранением и получением текущего прогресса просмотра фильма.

1. Set progress - сохранение прогресса просмотра фильма
2. Get progress - получение прогресса просмора фильма

А также функции для управления пользовательским контентом по фильмам:

1. Сreate user film - Создание документа в базе данных со связкой id пользователя и фильма

2. Add user film rating - Добавление рейтинга фильму юзером

3. Set user film bookmark - Добавление пользователем фильма в закладки

4. Add user film review - Добавление пользователем ревью по фильму

5. Get user film info - Получение пользовательского контента по фильму

6. Get movie avg rating - Получение среднего рейтинга фильма, на основании оценки пользователей

7. Delete user film info - Удаление пользовательского контента по фильму

**Хранение данных**

Для хранения прогресса просмотра используется Kafka, Redis.

Для хранения пользовательского контента по фильмам используется MongoDB.

Для аналитических задач, прогресс просмотра фильма также сохраняется в Clickhouse, а также реализован ETL процесс передачи данных из MongoDB в ClickHouse (см. дирректорию `mongodb`).


#  **Тесты**

Тесты работы api реализованы с помощью библиотеки pytest. Для запуска функциональных тестов необходимо:

В папке tests создать .env файл (пример расположен в файле tests/.env.example)
В консоли перейти в директорию tests и выполнить команду docker-compose up --build --exit-code-from ugc_tests

----


<details>
<summary>Установка poetry и запуск виртауального окружения</summary>


Для Linux, macOS, Windows (WSL):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
Для Windows (Powershell):
```bash
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```
В macOS и Windows сценарий установки предложит добавить папку с исполняемым файлом poetry в переменную PATH. Сделайте это, выполнив следующую команду:

macOS
```bash
export PATH=$PATH:$HOME/.local/bin
```
Windows
```bash
$Env:Path += ";C:\Users\jetbrains\AppData\Roaming\Python\Scripts"; setx PATH "$Env:Path"
```
Не забудьте поменять jetbrains на имя вашего пользователя. Настройка окружения poetry для pycharm [тут](https://www.jetbrains.com/help/pycharm/poetry.html)

Для проверки установки выполните следующую команду:
```bash
poetry --version
```
Установка автодополнений bash(опцонально)
```bash
poetry completions bash >> ~/.bash_completion
```

Изменить конфигурацию Poetry (опционально).

```shell
poetry config virtualenvs.in-project true
```
> **Note**:
> Позволяет создавать виртуальное окружение в папке проекта.

### Установка

1. Клонировать репозиторий.

    ```shell
    git clone https://github.com/StanleyOneG/ugc_sprint_1.git
    cd ugc_sprint_1
    ```

2. Создать и активировать виртуальное окружение.

    > **Warning**:
    > Необходимы для дальнейшей разработки приложения.

    ```shell
    poetry install
    poetry shell
    ```

3. Настроить pre-commit.

    ```shell
    pre-commit install --all
    ```
    > **Note**:
    > Перед каждым коммитом будет запущен линтер и форматтер,
    > который автоматически отформатирует код
    > согласно принятому в команде codestyle.

    > **Note**:
    > Если в процессе коммита линтер отформатирует код, коммит создан не будет,
    > а отформатированный файл отобразится в статусе *modified*.
    > В этом случае, необходимо добавить файл в *staged*
    > ```git add .```
    > и повторить коммит.

    > **Note**:
    > Если не видно какая ошибка мешает выполнить commit, то можно запустить хуки в ручную можно командой
    > ```bash
    > pre-commit run --all-files
    > ```

4. В дальнейшем для установки библиотек пользоваться командой:

    > ```bash
    > poetry add <libname>
    > ```

</details>
