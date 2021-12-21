from socialserver.tests.fixtures import mem_db, server_address
from datetime import datetime
import requests
from socialserver.db import create_memory_db
from pony.orm import db_session
from socialserver.constants import ErrorCodes, BIO_MAX_LEN
from secrets import token_urlsafe


def test_create_user(mem_db, server_address, monkeypatch):
    # create normal user
    monkeypatch.setattr("socialserver.api.v2.user.db", mem_db)
    user_creation_request = requests.post(f"{server_address}/api/v2/user",
                                          json={
                                              "display_name": "Test User",
                                              "username": "test",
                                              "password": "password",
                                          })
    assert user_creation_request.status_code.__int__() == 201


def test_create_user_with_bio(mem_db, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", mem_db)
    user_creation_request = requests.post(f"{server_address}/api/v2/user",
                                          json={
                                              "display_name": "Test User",
                                              "username": "test",
                                              "password": "password",
                                              "bio": "something goes here"
                                          })
    assert user_creation_request.status_code.__int__() == 201


def test_create_user_bio_too_long(mem_db, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", mem_db)
    user_creation_request = requests.post(f"{server_address}/api/v2/user",
                                          json={
                                              "display_name": "Test User",
                                              "username": "test",
                                              "password": "password",
                                              "bio": token_urlsafe(BIO_MAX_LEN + 1)
                                          })
    assert user_creation_request.status_code.__int__() == 400
    assert user_creation_request.json()['error'] == ErrorCodes.BIO_NON_CONFORMING.value


def test_attempt_create_duplicate_user(mem_db, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", mem_db)
    # create the user
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
    assert user_creation_request.status_code.__int__() == 400
    assert user_creation_request.json()['error'] == ErrorCodes.USERNAME_TAKEN.value


def test_create_user_missing_args(mem_db, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", mem_db)
    assert requests.post(f"{server_address}/api/v2/user", json={}).status_code == 400


def test_create_user_username_too_long(mem_db, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", mem_db)
    invalid_req = requests.post(f"{server_address}/api/v2/user",
                                json={
                                    "display_name": "Test User",
                                    "username": "idontknowwhattoputherebutitsgottabelong",
                                    "password": "password",
                                })
    assert invalid_req.status_code == 400
    assert invalid_req.json()['error'] == ErrorCodes.USERNAME_INVALID.value
