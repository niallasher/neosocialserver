# pycharm isn't detecting fixture usage, so we're
# disabling PyUnresolvedReferences for the import.
# noinspection PyUnresolvedReferences
from socialserver.util.test import test_db, server_address
from socialserver.constants import ErrorCodes
import requests


def test_create_session(test_db, server_address, monkeypatch):
    creation_req = requests.post(f"{server_address}/api/v3/user/session",
                                 json={
                                     "username": test_db.username,
                                     "password": test_db.password
                                 })

    assert creation_req.status_code == 200


def test_create_session_invalid_password(test_db, server_address, monkeypatch):
    creation_req = requests.post(f"{server_address}/api/v3/user/session",
                                 json={
                                     "username": test_db.username,
                                     "password": "invalid_password"
                                 })

    assert creation_req.status_code == 401
    assert creation_req.json()['error'] == ErrorCodes.INCORRECT_PASSWORD.value


def test_create_session_invalid_username(test_db, server_address, monkeypatch):
    creation_req = requests.post(f"{server_address}/api/v3/user/session",
                                 json={
                                     "username": "userdoesntexist",
                                     "password": test_db.password
                                 })

    assert creation_req.status_code == 404
    assert creation_req.json()['error'] == ErrorCodes.USERNAME_NOT_FOUND.value


def test_create_session_missing_data(test_db, server_address, monkeypatch):
    creation_req = requests.post(f"{server_address}/api/v3/user/session",
                                 json={})

    assert creation_req.status_code == 400


def test_get_user_session_info(test_db, server_address, monkeypatch):
    info_req = requests.get(f"{server_address}/api/v3/user/session",
                            headers={
                                "Authorization": f"Bearer {test_db.access_token}"
                            })

    assert info_req.status_code == 200
    assert info_req.json()['owner'] == test_db.username


def test_get_user_session_info_invalid(test_db, server_address, monkeypatch):
    info_req = requests.get(f"{server_address}/api/v3/user/session",
                            headers={
                                "Authorization": f"Bearer invalid"
                            })

    assert info_req.status_code == 401
    assert info_req.json()['error'] == ErrorCodes.TOKEN_INVALID.value


def test_get_user_session_list(test_db, server_address):
    r = requests.get(f"{server_address}/api/v3/user/session/list",
                     headers={
                         "Authorization": f"Bearer {test_db.access_token}"
                     })
    print(r.json())
    assert r.status_code == 200


def test_get_user_session_list_invalid_auth(test_db, server_address):
    r = requests.get(f"{server_address}/api/v3/user/session/list",
                     headers={
                         "Authorization": f"Bearer invalid"
                     })
    assert r.status_code == 401
