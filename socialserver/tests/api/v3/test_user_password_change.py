#  Copyright (c) Niall Asher 2022

from socialserver.util.test import test_db, server_address, create_user_with_request
from socialserver.constants import MIN_PASSWORD_LEN, MAX_PASSWORD_LEN, ErrorCodes
import requests


def test_change_user_password(test_db, server_address):
    # change the password from test_db default
    r = requests.patch(
        f"{server_address}/api/v3/user/password",
        headers={"Authorization": f"bearer {test_db.access_token}"},
        json={
            "old_password": test_db.password,
            # very secure.
            "new_password": "password1",
        },
    )
    assert r.status_code == 201

    # try to log in with the old one
    r = requests.post(
        f"{server_address}/api/v3/user/session",
        json={"username": test_db.username, "password": test_db.password},
    )

    assert r.status_code == 401

    # now with the actual correct one
    r = requests.post(
        f"{server_address}/api/v3/user/session",
        json={"username": test_db.username, "password": "password1"},
    )

    assert r.status_code == 200


def test_change_user_password_invalid_old_password(test_db, server_address):
    r = requests.patch(
        f"{server_address}/api/v3/user/password",
        headers={"Authorization": f"bearer {test_db.access_token}"},
        json={
            "old_password": "hunter2",
            # very secure.
            "new_password": "password1",
        },
    )
    assert r.status_code == 401
    assert r.json()["error"] == ErrorCodes.INCORRECT_PASSWORD.value


def test_change_user_password_new_password_too_short(test_db, server_address):
    r = requests.patch(
        f"{server_address}/api/v3/user/password",
        headers={"Authorization": f"bearer {test_db.access_token}"},
        json={
            "old_password": test_db.password,
            # very secure.
            "new_password": "a" * (MIN_PASSWORD_LEN - 1),
        },
    )
    assert r.status_code == 400
    assert r.json()["error"] == ErrorCodes.PASSWORD_NON_CONFORMING.value


def test_change_user_password_new_password_too_long(test_db, server_address):
    r = requests.patch(
        f"{server_address}/api/v3/user/password",
        headers={"Authorization": f"bearer {test_db.access_token}"},
        json={
            "old_password": test_db.password,
            # very secure.
            "new_password": "a" * (MAX_PASSWORD_LEN + 1),
        },
    )
    assert r.status_code == 400
    assert r.json()["error"] == ErrorCodes.PASSWORD_NON_CONFORMING.value


def test_change_password_remove_other_sessions(test_db, server_address):
    # list to store tokens; we want to loop over it and make sure
    # they're all invalid after the password change.
    # the first token should stay valid, since we're using it to
    # change the password.
    other_session_tokens = []
    # create 10 extra sessions
    for i in range(0, 10):
        r = requests.post(f"{server_address}/api/v3/user/session",
                          json={
                              "username": test_db.username,
                              "password": test_db.password
                          })
        other_session_tokens.append(r.json()['access_token'])
    r = requests.patch(f"{server_address}/api/v3/user/password",
                       json={
                           "old_password": test_db.password,
                           "new_password": "password1",  # very secure
                           "delete_other_sessions": True
                       },
                       headers={"Authorization": f"bearer {test_db.access_token}"})
    assert r.status_code == 201
    # check that none of the other tokens work.
    for i in other_session_tokens:
        r = requests.patch(f"{server_address}/api/v3/user/password",
                           json={
                               # we want the right password here,
                               # because we're just checking the session token
                               "old_password": "password1",
                               "new_password": "password2"
                           },
                           headers={
                               "Authorization": f"bearer {i}"
                           })
        assert r.status_code == 401
    # check that the original token still works
    r = requests.patch(f"{server_address}/api/v3/user/password",
                       json={
                           "old_password": "password1",
                           "new_password": "password2"
                       },
                       headers={
                           "Authorization": f"bearer {test_db.access_token}"
                       })
    assert r.status_code == 201
