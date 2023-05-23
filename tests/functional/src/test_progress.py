import json
from http import HTTPStatus
from functools import lru_cache

from .. import settings


@lru_cache
def get_test_settings():
    return settings.TestSettings()


test_settings = get_test_settings()


def test_set_progress(post_request, generate_movie_id, generate_timestamp, generate_cookies):
    """Set movie watch progress."""
    cookies = generate_cookies
    data = {'movie_id': generate_movie_id, 'timestamp': generate_timestamp}
    result = post_request(test_settings.service_url, '/api/v1/set_progress', data, cookies)
    assert result.status_code == HTTPStatus.OK


def test_get_progress(post_request, generate_movie_id, generate_timestamp, generate_cookies):
    """Get movies watch progress."""
    cookies = generate_cookies
    data = {'movie_id': generate_movie_id, 'timestamp': generate_timestamp}
    post_request(test_settings.service_url, '/api/v1/set_progress', data, cookies)

    result = post_request(
        test_settings.service_url, '/api/v1/get_progress', json.dumps({'movie_ids': [generate_movie_id]}), cookies
    )
    result_data = result.json()
    assert len(result_data) > 0
    assert result_data[0].get(generate_movie_id) == generate_timestamp
    assert result.status_code == HTTPStatus.OK
