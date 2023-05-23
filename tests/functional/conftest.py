"""Module for pytest fixtures."""
import random
import uuid
from datetime import datetime, timedelta
from typing import Optional
from functools import lru_cache

import pytest
import requests
from jose import jwt

from . import settings

TEST_USER_EMAIL = 'admin@admin.com'
TEST_USER_PASSWORD = 'admin'
TEST_USER_LOGIN = 'admin'


@lru_cache
def get_test_settings():
    return settings.TestSettings()


test_settings = get_test_settings()


@pytest.fixture
def post_request():
    """Fixture for making POST requests."""

    def _post_request(service_url: str, endpoint: str, data: Optional[dict] = None, cookies: Optional[dict] = None):
        url = service_url + endpoint
        return requests.post(url, data=data, cookies=cookies)

    return _post_request


@pytest.fixture
def generate_movie_id():
    """Generate a random movie id."""
    return str(uuid.uuid4())


@pytest.fixture
def generate_timestamp():
    """Generate a random timestamp."""
    return random.randint(0, 999999)


@pytest.fixture
def token():
    """Generate a JWT token."""
    to_encode = {}
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    to_encode.update({'permissions': ['subscriber']})
    to_encode.update({'sub': str(uuid.uuid4())})
    encoded_jwt = jwt.encode(to_encode, test_settings.jwt_private_key, algorithm='RS256')

    return encoded_jwt


@pytest.fixture
def generate_cookies(token):
    """Generate a cookie."""
    return {'access_token_cookie': token}
