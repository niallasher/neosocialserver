#  Copyright (c) Niall Asher 2022

# noinspection PyUnresolvedReferences
from time import sleep

from socialserver.util.config import config
from socialserver.util.test import test_db, server_address
from socialserver.constants import LegacyErrorCodes
import requests


def test_sign_in_legacy(test_db, server_address):
    r = requests.post(
        f"{server_address}/api/v1/auth",
        json={"username": test_db.username, "password": test_db.password},
    )
    assert r.status_code == 200


def test_sign_in_invalid_password_legacy(test_db, server_address):
    r = requests.post(
        f"{server_address}/api/v1/auth",
        json={"username": test_db.username, "password": "not quite right!"},
    )
    assert r.status_code == 401
    # error doesn't make any sense, but it has to be this, since
    # the old server returned the wrong error here. (PA03 instead of PA01)
    assert r.json()["err"] == LegacyErrorCodes.PASSWORD_DAMAGED.value


def test_sign_in_invalid_username_legacy(test_db, server_address):
    r = requests.post(
        f"{server_address}/api/v1/auth",
        json={"username": "does_not_exist", "password": test_db.password},
    )
    assert r.status_code == 404
    assert r.json()["err"] == LegacyErrorCodes.USERNAME_NOT_FOUND.value


def test_delete_session_legacy(test_db, server_address):
    r = requests.delete(
        f"{server_address}/api/v1/auth", json={"session_token": test_db.access_token}
    )
    assert r.status_code == 200
    # we're making another request with the token, and checking
    # we aren't authenticated, just to make sure they're actually
    # deleted!
    r2 = requests.get(
        f"{server_address}/api/v1/users",
        json={"session_token": test_db.access_token, "username": test_db.username},
    )
    assert r2.status_code == 401


def test_delete_session_invalid_token_legacy(test_db, server_address):
    r = requests.delete(
        f"{server_address}/api/v1/auth",
        json={"session_token": "making_this_up_as_i_go"},
    )
    assert r.status_code == 401


def test_account_lock_legacy(test_db, server_address):
    fail_lock_enabled_prev = config.auth.failure_lock.enabled
    fail_lock_time_prev = config.auth.failure_lock.lock_time_seconds
    fail_lock_count_prev = config.auth.failure_lock.fail_count_before_lock
    config.auth.failure_lock.enabled = True
    # as low as it can go for test speed
    config.auth.failure_lock.lock_time_seconds = 1
    config.auth.failure_lock.fail_count_before_lock = 5

    for i in range(0, 10):
        r = requests.post(f"{server_address}/api/v1/auth",
                          json={
                              "username": test_db.username,
                              "password": "invalid_password"
                          })
        assert r.status_code == 401
    r = requests.post(f"{server_address}/api/v1/auth",
                      json={
                          "username": test_db.username,
                          "password": "still_not_a valid password why did i not use spaces they're supported"
                      })
    assert r.status_code == 401
    assert r.json()["err"] == LegacyErrorCodes.GENERIC_SERVER_ERROR.value
    # we need to wait for the lock to expire. just be thankful the test doesn't set it to 15 minutes.
    sleep(1)
    r = requests.post(f"{server_address}/api/v1/auth",
                      json={
                          "username": test_db.username,
                          "password": test_db.password
                      })
    assert r.status_code == 200
    # reset things
    config.auth.failure_lock.enabled = fail_lock_enabled_prev
    config.auth.failure_lock.lock_time_seconds = fail_lock_time_prev
    config.auth.failure_lock.fail_count_before_lock = fail_lock_count_prev