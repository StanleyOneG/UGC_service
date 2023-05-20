from http import HTTPStatus
import uuid
import random


def test_set_progress(post_request, do_test_user_register):
    """Set movie watch progress"""
    r = do_test_user_register
    cookies = r.cookies
    data = {
        "film_id": '_'.join([str(uuid.uuid4()), str(uuid.uuid4())]),
        "timecode": random.randint(0, 9223372036854775807)
    }
    result = post_request('/api/v1/set_progress', data, cookies)
    assert result.status_code == HTTPStatus.OK


# def test_get_progress(post_request):
#     """Get movies watch progress"""
#     data = {
#         "id": random.randint(0, 4294967295),
#         "user_movie_id": uuid.uuid4() + '_' + uuid.uuid4(),
#         "timestamp": random.randint(0, 9223372036854775807)
#     }
#     post_request('/api/v1/set_progress', data)
#
#     result = post_request('/api/v1/get_progress',
#                           {"film_ids": [data.get('user_movie_id')]})
#     result_data = result.json()
#     assert result.status_code == HTTPStatus.OK
#
