#  Copyright (c) Niall Asher 2022

# noinspection PyUnresolvedReferences
from socialserver.util.test import test_db, server_address
from socialserver.constants import LegacyErrorCodes
import requests


def test_sign_in_legacy(test_db, server_address):
    r = requests.post(f"{server_address}/api/v1/auth",
                      json={
                          "username": test_db.username,
                          "password": test_db.password
                      })
    assert r.status_code == 200


def test_sign_in_invalid_password_legacy(test_db, server_address):
    r = requests.post(f"{server_address}/api/v1/auth",
                      json={
                          "username": test_db.username,
                          "password": "not quite right!"
                      })
    assert r.status_code == 401
    # error doesn't make any sense, but it has to be this, since
    # the old server returned the wrong error here. (PA03 instead of PA01)
    assert r.json()['err'] == LegacyErrorCodes.PASSWORD_DAMAGED.value


def test_sign_in_invalid_username_legacy(test_db, server_address):
    r = requests.post(f"{server_address}/api/v1/auth",
                      json={
                          "username": "does_not_exist",
                          "password": test_db.password
                      })
    assert r.status_code == 404
    assert r.json()['err'] == LegacyErrorCodes.USERNAME_NOT_FOUND.value


def test_delete_session_legacy(test_db, server_address):
    r = requests.delete(f"{server_address}/api/v1/auth",
                        json={
                            "session_token": test_db.access_token
                        })
    assert r.status_code == 200
    # we're making another request with the token, and checking
    # we aren't authenticated, just to make sure they're actually
    # deleted!
    r2 = requests.get(f"{server_address}/api/v1/users",
                      json={
                          "session_token": test_db.access_token,
                          "username": test_db.username
                      })
    assert r2.status_code == 401


def test_delete_session_invalid_token_legacy(test_db, server_address):
    r = requests.delete(f"{server_address}/api/v1/auth",
                        json={
                            "session_token": "making_this_up_as_i_go"
                        })
    assert r.status_code == 401
