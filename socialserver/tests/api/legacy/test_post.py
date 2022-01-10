from socialserver.util.test import test_db, server_address, create_post_with_request
import requests
from socialserver.constants import LegacyErrorCodes, MAX_FEED_GET_COUNT


def test_get_post_feed_legacy(test_db, server_address):
    post_id = create_post_with_request(server_address, auth_token=test_db.access_token, text_content="test")
    r = requests.get(f"{server_address}/api/v1/posts",
                     json={
                         "session_token": test_db.access_token,
                         "count": 10,
                         "offset": 0
                     })
    assert r.status_code == 201
    assert r.json()[0] == post_id
    assert len(r.json()) == 1


def test_get_post_feed_count_too_high_legacy(test_db, server_address):
    post_id = create_post_with_request(server_address, auth_token=test_db.access_token, text_content="test")
    r = requests.get(f"{server_address}/api/v1/posts",
                     json={
                         "session_token": test_db.access_token,
                         "count": MAX_FEED_GET_COUNT + 1,
                         "offset": 0
                     })
    assert r.status_code == 400


def test_get_post_feed_count_missing_args_legacy(test_db, server_address):
    post_id = create_post_with_request(server_address, auth_token=test_db.access_token, text_content="test")
    r = requests.get(f"{server_address}/api/v1/posts",
                     json={
                         "session_token": test_db.access_token,
                     })
    assert r.status_code == 400


def test_get_post_individual_legacy(test_db, server_address):
    post_id = create_post_with_request(server_address, auth_token=test_db.access_token, text_content="test")
    r = requests.get(f"{server_address}/api/v1/posts",
                     json={
                         "session_token": test_db.access_token,
                         "post_id": post_id
                     })
    assert r.status_code == 201
    assert r.json()['postText'] == 'test'


def test_get_post_individual_invalid_id_legacy(test_db, server_address):
    post_id = create_post_with_request(server_address, auth_token=test_db.access_token, text_content="test")
    r = requests.get(f"{server_address}/api/v1/posts",
                     json={
                         "session_token": test_db.access_token,
                         "post_id": 377
                     })
    # this hurts my soul, but yes, it has to be 401
    # for compatibility reasons!
    assert r.status_code == 401
    assert r.json()['err'] == LegacyErrorCodes.POST_NOT_FOUND.value


def test_create_post_legacy(test_db, server_address):
    r = requests.post(f"{server_address}/api/v1/posts",
                      json={
                          "session_token": test_db.access_token,
                          "post_text": "test"
                      })
    assert r.status_code == 201


def test_create_post_invalid_token_legacy(test_db, server_address):
    r = requests.post(f"{server_address}/api/v1/posts",
                      json={
                          "session_token": "invalid",
                          "post_text": "test"
                      })
    assert r.status_code == 401


def test_create_post_missing_args_legacy(test_db, server_address):
    r = requests.post(f"{server_address}/api/v1/posts",
                      json={
                          "session_token": test_db.access_token
                      })
    assert r.status_code == 400
