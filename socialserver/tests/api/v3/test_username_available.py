#  Copyright (c) Niall Asher 2022

# noinspection PyUnresolvedReferences
from socialserver.util.test import test_db, server_address
from socialserver.constants import ErrorCodes
import requests


def test_username_available_name_taken(test_db, server_address):
    r = requests.get(f"{server_address}/api/v3/usernameAvailable",
                     json={
                         "username": test_db.username
                     })

    assert r.status_code == 200
    assert r.json() is False


def test_username_available_name_not_taken(test_db, server_address):
    r = requests.get(f"{server_address}/api/v3/usernameAvailable",
                     json={
                         "username": "username"
                     })

    assert r.status_code == 200
    assert r.json() is True


def test_username_available_username_invalid(test_db, server_address):
    r = requests.get(f"{server_address}/api/v3/usernameAvailable",
                     json={
                         "username": "invalid username"
                     })

    assert r.status_code == 400
    assert r.json()['error'] == ErrorCodes.USERNAME_INVALID.value


def test_username_available_missing_data(test_db, server_address):
    r = requests.get(f"{server_address}/api/v3/usernameAvailable", json={})

    assert r.status_code == 400
