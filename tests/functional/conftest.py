"""Module for pytest fixtures."""
from typing import Optional
import requests

import pytest

from .settings import test_settings


@pytest.fixture
def post_request():
    def _post_request(endpoint: str, data: Optional[dict] = None):
        url = test_settings.service_url + endpoint
        return requests.post(url, data=data)
    return _post_request
