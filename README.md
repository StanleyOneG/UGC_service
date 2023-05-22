#  **Ссылка на репозиторий** https://github.com/StanleyOneG/ugc_sprint_1


#  **Ссылка на репозиторий Async_API** https://github.com/VladIs10ve/Async_API_sprint_1_team

#  **Ссылка на репозиторий Auth_API** https://github.com/VladIs10ve/Auth_sprint_1

Для интеграции сервисов используется jwt token и общий public_key

#  **Описание**

Это API реализует сохранение и получение прогресса просмотра фильма пользователей.

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
KAFKA_TOPIC=movie_progress
KAFKA_HOST=broker
KAFKA_PORT=9092

# Параметры базы данных REDIS
REDIS_HOST=redis_ugc
REDIS_PORT=6379

# Общие параметры сервиса
PROJECT_NAME="UGC"
PROJECT_DESCRIPTION="API для записи прогресса просмотра контента"
PROJECT_VERSION="1.0.0"
PROJECT_CACHE_SERVICE_NAME="redis"

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

Для запуска приложения необходимо запустить по очередь следующие файлы `docker-compose`:
- kakfa/docker-compose up --build
- etl-kafka/docker-compose up --build
- ugc_api/docker-compose up --build

Для остановки проекта используйте команду `docker-compose down`.

#  **API**

**Документация в формате OpenAPI:**

Документация API доступна в формате OpenAPI по адресу http://localhost:89/api/openapi/

***Реализованный функционал***

API предоставляет набор функций для работы с сохранением и получением текущего прогресса просмотра фильма.

1. Set progress - сохранение прогресса просмотра фильма
2. Get progress - получение прогресса просмора фильма

**Хранение данных**

Для хранения прогресса просмотра используется Kafka, Redis. Для аналитических задач, прогресс просмотра фильма также сохраняется в Clickhouse.

#  **Как начать**

Для начала работы с API необходимо выполнить следующие шаги:

1. Зарегистрировать или аутентифицировать пользователя в сервисе Auth для получения access и refresh токены
2. Использовать полученный access токен для выполнения запросов к API
3. При необходимости обновить access токен с помощью функции Refresh access token в сервисе Auth

Токены хранятся в cookies браузера


#  **Тесты**

Тесты работы api реализованы с помощью библиотеки pytest. Для запуска функциональных тестов необходимо:

В папке tests создать .env файл (пример расположен в файле tests/.env.example)
В консоли перейти в директорию tests и выполнить команду docker-compose up --build --exit-code-from ugc_tests
