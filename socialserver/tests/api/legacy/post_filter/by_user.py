from socialserver.util.test import test_db, server_address, create_post_with_request, create_user_with_request, \
    create_user_session_with_request
import requests
from socialserver.constants import MAX_FEED_GET_COUNT


def test_get_by_user_post_feed_for_user_legacy(test_db, server_address):
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


def test_get_by_user_post_feed_for_multiple_users_legacy(test_db, server_address):
    create_user_with_request(server_address, username="test2", password="password")
    create_user_with_request(server_address, username="test3", password="password")
    user_token = create_user_session_with_request(server_address, username="test2", password="password")
    user_token_2 = create_user_session_with_request(server_address, username="test3", password="password")

    post_id = create_post_with_request(server_address, user_token, text_content="test")
    post_id_2 = create_post_with_request(server_address, user_token_2, text_content="test")

    r = requests.get(f"{server_address}/api/v1/posts/byUser",
                     json={
                         "session_token": test_db.access_token,
                         "count": 10,
                         "offset": 0,
                         "users": ["test3", "test2"],
                     })

    assert r.status_code == 201
    # sorted by ID descending, so the first made post should be returned last
    print(r.json())
    assert r.json()[1] == post_id
    assert r.json()[0] == post_id_2


def test_get_by_user_post_feed_get_count_too_high_legacy(test_db, server_address):
    r = requests.get(f"{server_address}/api/v1/posts/byUser",
                     json={
                         "session_token": test_db.access_token,
                         "count": MAX_FEED_GET_COUNT + 1,
                         "offset": 0,
                         "users": ["test"]
                     })
    assert r.status_code == 400


def test_get_by_user_post_feed_invalid_usernames_legacy(test_db, server_address):
    r = requests.get(f"{server_address}/api/v1/posts/byUser",
                     json={
                         "session_token": test_db.access_token,
                         "count": 10,
                         "offset": 0,
                         "users": ["doesntexist"]
                     })
    assert r.status_code == 406


def test_get_by_user_post_feed_mixed_valid_invalid_users_legacy(test_db, server_address):
    create_user_with_request(server_address, username="test2", password="password")
    user_token = create_user_session_with_request(server_address, username="test2", password="password")
    post_id = create_post_with_request(server_address, user_token, text_content="test")

    r = requests.get(f"{server_address}/api/v1/posts/byUser",
                     json={
                         "session_token": test_db.access_token,
                         "count": 1,
                         "offset": 0,
                         "users": ["test2", "invalid_user"]
                     })

    assert r.status_code == 201
    assert len(r.json()) == 1
    assert r.json()[0] == post_id
