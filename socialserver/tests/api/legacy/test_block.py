#  Copyright (c) Niall Asher 2022

# noinspection PyUnresolvedReferences
from socialserver.util.test import test_db, server_address, create_post_with_request, create_user_with_request, \
    create_user_session_with_request
import requests


def test_block_user_legacy(test_db, server_address):
    # create somebody to get angry at
    create_user_with_request(server_address, username="test2", password="password")
    test2_session_token = create_user_session_with_request(server_address, username="test2", password="password")
    post_id = create_post_with_request(server_address, auth_token=test2_session_token,
                                       text_content="bad opinion i disagree with")
    # now block them
    r = requests.post(f"{server_address}/api/v1/block",
                      json={
                          "session_token": test_db.access_token,
                          "username": "test2"
                      })
    assert r.status_code == 201
    assert r.json()["userBlocked"] is True
    # get the post feed, and make sure this users post isn't included
    r = requests.get(f"{server_address}/api/v1/posts",
                     json={
                         "session_token": test_db.access_token,
                         "count": 10,
                         "offset": 0
                     })
    print(r.json())
    posts = r.json()
    assert post_id not in posts


def test_unblock_user_legacy(test_db, server_address):
    # create somebody to get angry at
    create_user_with_request(server_address, username="test2", password="password")
    test2_session_token = create_user_session_with_request(server_address, username="test2", password="password")
    post_id = create_post_with_request(server_address, auth_token=test2_session_token,
                                       text_content="bad opinion i disagree with")
    # now block them
    r = requests.post(f"{server_address}/api/v1/block",
                      json={
                          "session_token": test_db.access_token,
                          "username": "test2"
                      })
    assert r.status_code == 201
    assert r.json()["userBlocked"] is True
    # now unblock
    r = requests.post(f"{server_address}/api/v1/block",
                      json={
                          "session_token": test_db.access_token,
                          "username": "test2"
                      })
    assert r.status_code == 201
    assert r.json()["userBlocked"] is False
    # get the post feed, and make sure this users post *is* included
    r = requests.get(f"{server_address}/api/v1/posts",
                     json={
                         "session_token": test_db.access_token,
                         "count": 10,
                         "offset": 0
                     })
    print(r.json())
    posts = r.json()
    assert post_id in posts


def test_get_block_list_no_blocked_users_legacy(test_db, server_address):
    r = requests.get(f"{server_address}/api/v1/users/blockList",
                     json={
                         "session_token": test_db.access_token
                     })
    assert len(r.json()) == 0
    assert r.status_code == 201


def test_get_block_list_legacy(test_db, server_address):
    create_user_with_request(server_address, username="test2")
    # block the above bastard
    r = requests.post(f"{server_address}/api/v1/block",
                      json={
                          "session_token": test_db.access_token,
                          "username": "test2"
                      })
    r = requests.get(f"{server_address}/api/v1/users/blockList",
                     json={
                         "session_token": test_db.access_token
                     })
    assert len(r.json()) == 1
    # the user we created just before should be in the returned results
    assert r.json()[0]["username"] == "test2"
    assert r.status_code == 201
