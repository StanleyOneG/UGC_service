"""Module for pytest fixtures."""
from typing import Optional
import requests
import uuid
import random
# from contextlib import closing

import pytest

from .settings import test_settings

TEST_USER_EMAIL = 'admin@admin.com'
TEST_USER_PASSWORD = 'admin'
TEST_USER_LOGIN = 'admin'


@pytest.fixture
def post_request():
    def _post_request(service_url: str,
                      endpoint: str,
                      data: Optional[dict] = None,
                      cookies: Optional[dict] = None):
        url = service_url + endpoint
        return requests.post(url, data=data, cookies=cookies)
    return _post_request


@pytest.fixture
def do_test_user_login(post_request):
    def _do_test_user_login():
        data = {
                'email': TEST_USER_EMAIL,
                'password': TEST_USER_PASSWORD,
            }
        response = post_request(
            test_settings.auth_service_url,
            '/api/v1/user/login',
            data,
        )
        return response

    return _do_test_user_login


@pytest.fixture
def generate_movie_id():
    return str(uuid.uuid4())


@pytest.fixture
def generate_timestamp():
    return random.randint(0, 999999)


# @pytest.fixture
# def do_test_user_register(post_request):
#     def _do_test_user_register():
#         data = {
#                 'email': TEST_USER_EMAIL,
#                 'password': TEST_USER_PASSWORD,
#                 'login': TEST_USER_LOGIN,
#             }
#         response = post_request(
#             test_settings.auth_service_url + '/api/v1/login',
#             data,
#         )
#         return response

#     return _do_test_user_register


# @pytest.fixture(scope='module', autouse=True)
# def cleanup(request):
#     """Truncate cascade the auth.user table after tests per module."""

#     def _cleanup():
#         with closing(conn.cursor()) as cursor:
#             cursor.execute('TRUNCATE TABLE auth.user CASCADE')

#     request.addfinalizer(_cleanup)
