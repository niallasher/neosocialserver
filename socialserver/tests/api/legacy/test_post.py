#  Copyright (c) Niall Asher 2022

# noinspection PyUnresolvedReferences
from socialserver.util.test import test_db, server_address, create_post_with_request, create_user_with_request, \
    create_user_session_with_request
import requests
from socialserver.constants import LegacyErrorCodes, MAX_FEED_GET_COUNT
from secrets import token_urlsafe


def test_get_post_feed_legacy(test_db, server_address):
    post_id = create_post_with_request(auth_token=test_db.access_token, text_content="test")
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
    post_id = create_post_with_request(auth_token=test_db.access_token, text_content="test")
    r = requests.get(f"{server_address}/api/v1/posts",
                     json={
                         "session_token": test_db.access_token,
                         "count": MAX_FEED_GET_COUNT + 1,
                         "offset": 0
                     })
    assert r.status_code == 400


def test_get_post_feed_count_missing_args_legacy(test_db, server_address):
    post_id = create_post_with_request(auth_token=test_db.access_token, text_content="test")
    r = requests.get(f"{server_address}/api/v1/posts",
                     json={
                         "session_token": test_db.access_token,
                     })
    assert r.status_code == 400


def test_get_post_individual_legacy(test_db, server_address):
    post_id = create_post_with_request(auth_token=test_db.access_token, text_content="test")
    r = requests.get(f"{server_address}/api/v1/posts",
                     json={
                         "session_token": test_db.access_token,
                         "post_id": post_id
                     })
    assert r.status_code == 201
    assert r.json()['postText'] == 'test'


def test_get_post_individual_invalid_id_legacy(test_db, server_address):
    post_id = create_post_with_request(auth_token=test_db.access_token, text_content="test")
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


def test_create_post_too_long_legacy(test_db, server_address):
    r = requests.post(f"{server_address}/api/v1/posts",
                      json={
                          "session_token": test_db.access_token,
                          "post_text": token_urlsafe(1024)
                      })
    # shouldn't fail because v1 just truncates!
    assert r.status_code == 201


def test_create_post_missing_args_legacy(test_db, server_address):
    r = requests.post(f"{server_address}/api/v1/posts",
                      json={
                          "session_token": test_db.access_token
                      })
    assert r.status_code == 400


def test_delete_post_legacy(test_db, server_address):
    # create a post so that we can actually delete it :)
    post_id = create_post_with_request(test_db.access_token)

    r = requests.delete(f"{server_address}/api/v1/posts",
                        json={
                            "session_token": test_db.access_token,
                            "post_id": post_id
                        })

    assert r.status_code == 201


def test_delete_post_missing_args_legacy(test_db, server_address):
    # create a post so that we can actually delete it :)
    post_id = create_post_with_request(test_db.access_token)

    r = requests.delete(f"{server_address}/api/v1/posts",
                        json={
                            "session_token": test_db.access_token,
                        })

    assert r.status_code == 400


def test_delete_post_invalid_id_legacy(test_db, server_address):
    r = requests.delete(f"{server_address}/api/v1/posts",
                        json={
                            "session_token": test_db.access_token,
                            "post_id": 1337
                        })

    # yes, this should be a 404 logically, but IIRC the original client
    # doesn't actually handle a 404 here, which is why it's a 401, since that
    # was an explicitly handled case
    assert r.status_code == 401


def test_try_delete_other_users_post_legacy(test_db, server_address):
    create_user_with_request(username="other_user", password="password")
    user_token = create_user_session_with_request(username="other_user", password="password")
    # create a post under the other user!
    post_id = create_post_with_request(user_token)

    r = requests.delete(f"{server_address}/api/v1/posts",
                        json={
                            "session_token": test_db.access_token,
                            "post_id": post_id
                        })

    assert r.status_code == 401


def test_delete_post_invalid_token_legacy(test_db, server_address):
    post_id = create_post_with_request(test_db.access_token)

    r = requests.delete(f"{server_address}/api/v1/posts",
                        json={
                            "session_token": "abcxyz",
                            "post_id": post_id
                        })

    assert r.status_code == 401
