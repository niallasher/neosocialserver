# noinspection PyUnresolvedReferences
from socialserver.util.test import test_db_with_user, server_address, create_post_with_request
from socialserver.constants import ErrorCodes
import requests


def test_create_single_post(test_db_with_user, server_address, monkeypatch):
    r = requests.post(f"{server_address}/api/v2/post/single",
                      json={
                          "access_token": test_db_with_user.access_token,
                          "text_content": "Test Post"
                      })

    assert r.status_code == 200
    # blank database, so this should be post id 1.
    assert r.json()['post_id'] == 1


def test_create_single_post_missing_args(test_db_with_user, server_address, monkeypatch):
    r = requests.post(f"{server_address}/api/v2/post/single",
                      json={})

    assert r.status_code == 400


def test_create_single_post_invalid_access_token(test_db_with_user, server_address, monkeypatch):
    r = requests.post(f"{server_address}/api/v2/post/single",
                      json={
                          "access_token": "invalid_access_token",
                          "text_content": "Test Post"
                      })

    assert r.status_code == 401
    assert r.json()['error'] == ErrorCodes.TOKEN_INVALID.value


def test_get_single_post(test_db_with_user, server_address, monkeypatch):
    new_post_id = create_post_with_request(server_address,
                                           test_db_with_user.access_token)

    r = requests.get(f"{server_address}/api/v2/post/single",
                     json={
                         "access_token": test_db_with_user.get("access_token"),
                         "post_id": new_post_id
                     })

    assert r.status_code == 201
    assert r.json()['post']['id'] == new_post_id
    assert r.json()['user']['username'] == test_db_with_user.username


def test_get_single_post_not_exist(test_db_with_user, server_address, monkeypatch):
    r = requests.get(f"{server_address}/api/v2/post/single",
                     json={
                         "access_token": test_db_with_user.get("access_token"),
                         # we're on a blank database. 1 shouldn't exist.
                         "post_id": 1
                     })

    assert r.status_code == 404
    assert r.json()['error'] == ErrorCodes.POST_NOT_FOUND.value


def test_get_single_post_invalid_access_token(test_db_with_user, server_address, monkeypatch):
    new_post_id = create_post_with_request(server_address,
                                           test_db_with_user.access_token)

    r = requests.get(f"{server_address}/api/v2/post/single",
                     json={
                         "access_token": "invalid token",
                         "post_id": new_post_id
                     })

    assert r.status_code == 401
    assert r.json()['error'] == ErrorCodes.TOKEN_INVALID.value


def test_get_single_post_missing_args(test_db_with_user, server_address, monkeypatch):
    create_post_with_request(server_address,
                             test_db_with_user.access_token)

    r = requests.get(f"{server_address}/api/v2/post/single",
                     json={})

    assert r.status_code == 400
