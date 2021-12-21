from socialserver.tests.util import test_db, server_address, create_test_user_api2, test_db_with_user
from datetime import datetime
import requests
from socialserver.db import create_test_db, define_entities
from socialserver import api
from pony.orm import db_session
from socialserver.constants import ErrorCodes, BIO_MAX_LEN
from secrets import token_urlsafe


def test_create_user(test_db, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db)

    user_creation_request = requests.post(f"{server_address}/api/v2/user",
                                          json={
                                              "display_name": "Test User",
                                              "username": "test",
                                              "password": "password",
                                          })
    print(user_creation_request.json())
    assert user_creation_request.status_code.__int__() == 201
    test_db.drop_all_tables(with_all_data=True)

def test_create_user_with_bio(test_db, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db)
    user_creation_request = requests.post(f"{server_address}/api/v2/user",
                                          json={
                                              "display_name": "Test User",
                                              "username": "test",
                                              "password": "password",
                                              "bio": "something goes here"
                                          })
    assert user_creation_request.status_code.__int__() == 201


def test_create_user_bio_too_long(test_db, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db)
    user_creation_request = requests.post(f"{server_address}/api/v2/user",
                                          json={
                                              "display_name": "Test User",
                                              "username": "test",
                                              "password": "password",
                                              "bio": token_urlsafe(BIO_MAX_LEN + 1)
                                          })
    assert user_creation_request.status_code.__int__() == 400
    assert user_creation_request.json()['error'] == ErrorCodes.BIO_NON_CONFORMING.value


@db_session
def test_attempt_create_duplicate_user(test_db, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db)
    requests.post(f"{server_address}/api/v2/user",
                  json={
                      "display_name": "Test User",
                      "username": "test",
                      "password": "password",
                  })
    user_creation_request = requests.post(f"{server_address}/api/v2/user",
                                          json={
                                              "display_name": "Test User",
                                              "username": "test",
                                              "password": "password",
                                          })
    print(user_creation_request.json())
    assert user_creation_request.status_code.__int__() == 400
    assert user_creation_request.json()['error'] == ErrorCodes.USERNAME_TAKEN.value


def test_create_user_missing_args(test_db, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db)
    assert requests.post(f"{server_address}/api/v2/user", json={}).status_code == 400


def test_create_user_username_too_long(test_db, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db)
    invalid_req = requests.post(f"{server_address}/api/v2/user",
                                json={
                                    "display_name": "Test User",
                                    "username": "idontknowwhattoputherebutitsgottabelong",
                                    "password": "password",
                                })
    assert invalid_req.status_code == 400
    assert invalid_req.json()['error'] == ErrorCodes.USERNAME_INVALID.value

def test_delete_user(test_db_with_user, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db_with_user.get('db'))
    monkeypatch.setattr("socialserver.util.auth.db", test_db_with_user.get('db'))
    print(test_db_with_user.get('access_token'))
    del_req = requests.delete(f"{server_address}/api/v2/user",
                              json={
                                  "access_token": test_db_with_user.get('access_token'),
                                  "password": test_db_with_user.get('password')
                              })
    print(del_req.json())
    assert del_req.status_code == 200