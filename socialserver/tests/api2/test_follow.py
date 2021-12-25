# noinspection PyUnresolvedReferences
from socialserver.util.test import test_db, server_address, create_user_with_request, follow_user_with_request
from socialserver.constants import ErrorCodes
import requests


def test_follow_user(test_db, server_address):
    create_user_with_request(server_address, username="user2")
    r = requests.post(f"{server_address}/api/v2/follow/user",
                      json={
                          "access_token": test_db.access_token,
                          "username": "user2"
                      })
    assert r.status_code == 201


def test_follow_user_already_followed(test_db, server_address):
    create_user_with_request(server_address, username="user2")
    follow_user_with_request(server_address, test_db.access_token, username="user2")
    r = requests.post(f"{server_address}/api/v2/follow/user",
                      json={
                          "access_token": test_db.access_token,
                          "username": "user2"
                      })
    assert r.status_code == 400
    assert r.json()['error'] == ErrorCodes.FOLLOW_ALREADY_EXISTS.value


def test_unfollow_user(test_db, server_address):
    create_user_with_request(server_address, username="user2")
    follow_user_with_request(server_address, test_db.access_token, username="user2")
    r = requests.delete(fr"{server_address}/api/v2/follow/user",
                        json={
                            "access_token": test_db.access_token,
                            "username": "user2"
                        })
    assert r.status_code == 204


def test_unfollow_user_not_followed(test_db, server_address):
    create_user_with_request(server_address, username="user2")
    r = requests.delete(f"{server_address}/api/v2/follow/user",
                        json={
                            "access_token": test_db.access_token,
                            "username": "user2"
                        })
    assert r.status_code == 404
    assert r.json()['error'] == ErrorCodes.CANNOT_FIND_FOLLOW_ENTRY.value


def test_try_follow_self(test_db, server_address):
    r = requests.post(f"{server_address}/api/v2/follow/user",
                      json={
                          "access_token": test_db.access_token,
                          "username": "test"
                      })
    assert r.status_code == 400
    assert r.json()['error'] == ErrorCodes.CANNOT_FOLLOW_SELF.value


def test_try_follow_non_existent_user(test_db, server_address):
    r = requests.post(f"{server_address}/api/v2/follow/user",
                      json={
                          "access_token": test_db.access_token,
                          "username": "non_existent_user"
                      })
    assert r.status_code == 404
    assert r.json()['error'] == ErrorCodes.USERNAME_NOT_FOUND.value


def test_follow_user_invalid_token(test_db, server_address):
    create_user_with_request(server_address, username="user1")
    r = requests.post(f"{server_address}/api/v2/follow/user",
                      json={
                          "access_token": "invalid_token",
                          "username": "user1"
                      })
    assert r.status_code == 401
    assert r.json()['error'] == ErrorCodes.TOKEN_INVALID.value