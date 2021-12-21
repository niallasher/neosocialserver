from socialserver.tests.util import test_db_with_user, server_address
from socialserver.constants import ErrorCodes
import requests


def test_create_session(test_db_with_user, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.usersession.db", test_db_with_user.get('db'))
    monkeypatch.setattr("socialserver.util.auth.db", test_db_with_user.get('db'))

    creation_req = requests.post(f"{server_address}/api/v2/user/session",
                                 json={
                                     "username": test_db_with_user.get('username'),
                                     "password": test_db_with_user.get('password')
                                 })

    assert creation_req.status_code == 200


def test_create_session_invalid_password(test_db_with_user, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.usersession.db", test_db_with_user.get('db'))
    monkeypatch.setattr("socialserver.util.auth.db", test_db_with_user.get('db'))

    creation_req = requests.post(f"{server_address}/api/v2/user/session",
                                 json={
                                     "username": test_db_with_user.get('username'),
                                     "password": "invalid_password"
                                 })

    assert creation_req.status_code == 401
    assert creation_req.json()['error'] == ErrorCodes.INCORRECT_PASSWORD.value


def test_create_session_invalid_username(test_db_with_user, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.usersession.db", test_db_with_user.get('db'))
    monkeypatch.setattr("socialserver.util.auth.db", test_db_with_user.get('db'))

    creation_req = requests.post(f"{server_address}/api/v2/user/session",
                                 json={
                                     "username": "userdoesntexist",
                                     "password": test_db_with_user.get('password')
                                 })

    assert creation_req.status_code == 404
    assert creation_req.json()['error'] == ErrorCodes.USERNAME_NOT_FOUND.value


def test_create_session_missing_data(test_db_with_user, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.usersession.db", test_db_with_user.get('db'))
    monkeypatch.setattr("socialserver.util.auth.db", test_db_with_user.get('db'))

    creation_req = requests.post(f"{server_address}/api/v2/user/session",
                                 json={})

    assert creation_req.status_code == 400
