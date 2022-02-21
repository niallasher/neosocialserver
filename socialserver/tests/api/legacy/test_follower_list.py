#  Copyright (c) Niall Asher 2022

# noinspection PyUnresolvedReferences
from socialserver.util.test import create_user_with_request, follow_user_with_request, server_address, \
    test_db, create_user_session_with_request
import requests


def test_get_following_legacy(test_db, server_address):
    usernames = ['test2', 'test3', 'test4', 'test5']
    # create & follow a few of accounts
    for username in usernames:
        create_user_with_request(server_address, username=username)
        follow_user_with_request(server_address, test_db.access_token, username)

    r = requests.get(f"{server_address}/api/v1/followers/userFollows",
                     json={
                         "session_token": test_db.access_token,
                         "username": test_db.username
                     })

    assert r.status_code == 201
    assert len(r.json()) == 4
    for username in usernames:
        assert username in r.json()


def test_get_following_no_users_legacy(test_db, server_address):
    r = requests.get(f"{server_address}/api/v1/followers/userFollows",
                     json={
                         "session_token": test_db.access_token,
                         "username": test_db.username
                     })

    assert r.status_code == 201
    assert len(r.json()) == 0


def test_get_following_invalid_username(test_db, server_address):
    r = requests.get(f"{server_address}/api/v1/followers/userFollows",
                     json={
                         "session_token": test_db.access_token,
                         "username": "invalid"
                     })

    assert r.status_code == 404


def test_get_followers_invalid_usernames(test_db, server_address):
    usernames = ['test2', 'test3', 'test4', 'test5']
    # create & follow a few accounts
    for username in usernames:
        create_user_with_request(server_address, username=username)
        # password is the default!
        token = create_user_session_with_request(server_address, username=username, password="password")
        follow_user_with_request(server_address, token, test_db.username)

    r = requests.get(f"{server_address}/api/v1/followers/followsUser",
                     json={
                         "session_token": test_db.access_token,
                         "username": test_db.username
                     })

    assert r.status_code == 201
    assert len(r.json()) == 4
    for username in usernames:
        assert username in r.json()


def test_get_followers_no_users_legacy(test_db, server_address):
    r = requests.get(f"{server_address}/api/v1/followers/followsUser",
                     json={
                         "session_token": test_db.access_token,
                         "username": test_db.username
                     })

    assert r.status_code == 201
    assert len(r.json()) == 0


def test_get_followers_invalid_username(test_db, server_address):
    r = requests.get(f"{server_address}/api/v1/followers/followsUser",
                     json={
                         "session_token": test_db.access_token,
                         "username": "invalid"
                     })

    assert r.status_code == 404
