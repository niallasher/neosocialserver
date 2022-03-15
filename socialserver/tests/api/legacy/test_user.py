#  Copyright (c) Niall Asher 2022

# noinspection PyUnresolvedReferences
from socialserver.util.test import test_db, server_address
import requests
from socialserver.constants import LegacyErrorCodes, MAX_PASSWORD_LEN
from secrets import token_urlsafe


def test_create_user_legacy(test_db, server_address):
    r = requests.post(
        f"{server_address}/api/v1/users",
        json={"username": "testuser", "display_name": "test", "password": "password"},
    )

    print(r.json())
    assert r.status_code == 201


def test_create_user_already_exists_legacy(test_db, server_address):
    # test already exists as part of the test_db fixture!
    r = requests.post(
        f"{server_address}/api/v1/users",
        json={"username": "test", "display_name": "test", "password": "password"},
    )

    assert r.json()["err"] == LegacyErrorCodes.USERNAME_TAKEN.value
    assert r.status_code == 400


def test_create_user_missing_args_legacy(test_db, server_address):
    r = requests.post(f"{server_address}/api/v1/users", json={})

    assert r.status_code == 400


def test_create_user_username_too_long_legacy(test_db, server_address):
    r = requests.post(
        f"{server_address}/api/v1/users",
        json={
            "username": "very_long_username_that_is_invalid",
            "display_name": "test",
            "password": "password",
        },
    )

    print(r.json())
    assert r.status_code == 400


def test_create_user_password_too_short_legacy(test_db, server_address):
    r = requests.post(
        f"{server_address}/api/v1/users",
        json={"username": "testuser", "display_name": "test", "password": "p"},
    )

    print(r.json())
    assert r.status_code == 400


def test_create_user_password_too_long_legacy(test_db, server_address):
    r = requests.post(
        f"{server_address}/api/v1/users",
        json={
            "username": "testuser",
            "display_name": "test",
            "password": token_urlsafe(MAX_PASSWORD_LEN + 1),
        },
    )

    print(r.json())
    assert r.status_code == 400


def test_delete_user_legacy(test_db, server_address):
    r = requests.delete(
        f"{server_address}/api/v1/users",
        json={"session_token": test_db.access_token, "password": test_db.password},
    )

    assert r.status_code == 201


def test_delete_user_invalid_password_legacy(test_db, server_address):
    r = requests.delete(
        f"{server_address}/api/v1/users",
        json={"session_token": test_db.access_token, "password": "hunter2"},
    )

    assert r.status_code == 401


def test_delete_user_missing_args_legacy(test_db, server_address):
    r = requests.delete(f"{server_address}/api/v1/users", json={})

    assert r.status_code == 400


def test_delete_user_invalid_token_legacy(test_db, server_address):
    r = requests.delete(
        f"{server_address}/api/v1/users",
        json={"session_token": "invalid", "password": test_db.password},
    )

    assert r.status_code == 401


def test_get_user_legacy(test_db, server_address):
    r = requests.get(
        f"{server_address}/api/v1/users",
        json={"session_token": test_db.access_token, "username": test_db.username},
    )
    print(r.json())
    assert r.status_code == 200
    assert r.json()["username"] == test_db.username


def test_get_user_invalid_token_legacy(test_db, server_address):
    r = requests.get(
        f"{server_address}/api/v1/users",
        json={"session_token": "invalid", "username": test_db.username},
    )
    print(r.json())
    assert r.json()["err"] == LegacyErrorCodes.TOKEN_INVALID.value
    assert r.status_code == 401


def test_get_user_missing_username_legacy(test_db, server_address):
    r = requests.get(
        f"{server_address}/api/v1/users",
        json={"session_token": test_db.access_token, "username": "does_not_exist"},
    )
    assert r.status_code == 404


def test_get_user_missing_args_legacy(test_db, server_address):
    r = requests.get(f"{server_address}/api/v1/users", json={})
    assert r.status_code == 400
