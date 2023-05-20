"""Config."""

import os

from .backend_conf import Settings

configs = Settings()

PROJECT_NAME = configs.PROJECT.NAME
PROJECT_DESCRIPTION = configs.PROJECT.DESCRIPTION
PROJECT_VERSION = configs.PROJECT.VERSION
CACHE_SERVICE_NAME = configs.PROJECT.CACHE_SERVICE_NAME

REDIS_HOST = configs.REDIS.HOST
REDIS_PORT = configs.REDIS.PORT

JWT_PUBLIC_KEY = configs.JWT.PUBLIC_KEY

KAFKA_TOPIC = configs.KAFKA.TOPIC
KAFKA_HOST = configs.KAFKA.HOST
KAFKA_PORT = configs.KAFKA.PORT

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
