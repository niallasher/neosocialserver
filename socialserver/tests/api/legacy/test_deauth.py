#  Copyright (c) Niall Asher 2022

# noinspection PyUnresolvedReferences
from socialserver.util.test import (
    server_address,
    create_user_session_with_request,
    test_db,
)
import requests
from random import choice


def test_user_deauth_legacy(test_db, server_address):
    sessions = []
    # create some sessions
    for i in range(0, 10):
        sessions.append(
            create_user_session_with_request(
                username=test_db.username, password=test_db.password
            )
        )

    # revoke all sessions

    r = requests.post(
        f"{server_address}/api/v2/user/deauth",
        json={
            # use a random session token from the list
            "session_token": choice(sessions),
            "password": test_db.password,
        },
    )

    assert r.status_code == 201

    # make sure they're actually revoked
    for session_token in sessions:
        assert (
                requests.get(
                    f"{server_address}/api/v1/users",
                    json={"session_token": session_token, "username": test_db.username},
                ).status_code
                == 401
        )


def test_user_deauth_invalid_password_legacy(test_db, server_address):
    sessions = []
    # create some sessions
    for i in range(0, 10):
        sessions.append(
            create_user_session_with_request(
                username=test_db.username, password=test_db.password
            )
        )

    # attempt to revoke all sessions (should fail!)

    r = requests.post(
        f"{server_address}/api/v2/user/deauth",
        json={
            # use a random session token from the list
            "session_token": choice(sessions),
            "password": "invalid password",
        },
    )

    assert r.status_code == 401

    # make sure they're not revoked
    for session_token in sessions:
        assert (
                requests.get(
                    f"{server_address}/api/v1/users",
                    json={"session_token": session_token, "username": test_db.username},
                ).status_code
                != 401
        )
