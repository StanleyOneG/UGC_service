from http import HTTPStatus
import json

from ..settings import test_settings


def test_set_progress(post_request,
                      do_test_user_login,
                      generate_movie_id,
                      generate_timestamp):
    """Set movie watch progress"""
    r = do_test_user_login()
    cookies = r.cookies
    data = {
        "movie_id": generate_movie_id,
        "timestamp": generate_timestamp
    }
    result = post_request(test_settings.service_url,
                          '/api/v1/set_progress',
                          data,
                          cookies)
    assert result.status_code == HTTPStatus.OK


def test_get_progress(do_test_user_login,
                      post_request,
                      generate_movie_id,
                      generate_timestamp):
    """Get movies watch progress"""
    r = do_test_user_login()
    cookies = r.cookies
    data = {
        "movie_id": generate_movie_id,
        "timestamp": generate_timestamp
    }
    post_request(test_settings.service_url,
                 '/api/v1/set_progress',
                 data,
                 cookies)

    result = post_request(test_settings.service_url,
                          '/api/v1/get_progress',
                          json.dumps({"movie_ids": [generate_movie_id]}),
                          cookies)
    result_data = result.json()
    assert len(result_data) > 0
    assert result_data[0].get(generate_movie_id) == generate_timestamp
    assert result.status_code == HTTPStatus.OK
