from socialserver.util.test import test_db, server_address, create_post_with_request, create_user_with_request, \
    create_user_session_with_request
import requests
from socialserver.constants import MAX_FEED_GET_COUNT


def test_get_post_feed_for_user_legacy(test_db, server_address):
    create_user_with_request(server_address, username="test2", password="password")
    user_token = create_user_session_with_request(server_address, username="test2", password="password")
    post_id = create_post_with_request(server_address, user_token, text_content="test")

    r = requests.get(f"{server_address}/api/v1/posts/byUser",
                     json={
                         "session_token": test_db.access_token,
                         "count": 1,
                         "offset": 0,
                         "users": ["test2"]
                     })

    assert r.status_code == 201
    assert r.json()[0] == post_id