#  Copyright (c) Niall Asher 2022

from socialserver.util.test import test_db, server_address, create_user_with_request, follow_user_with_request, \
    create_user_session_with_request
from socialserver.constants import ErrorCodes, FollowListSortTypes
import requests


def test_get_following_list_empty(test_db, server_address):
    # create a user to be forever alone.
    create_user_with_request(username="user2")
    r = requests.get(f"{server_address}/api/v3/user/following",
                     json={
                         "sort_type": FollowListSortTypes.AGE_DESCENDING.value,
                         "username": "user2",
                         "count": 10,
                         "offset": 0
                     },
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200
    assert r.json()["meta"]["count"] == 0
    assert r.json()["meta"]["reached_end"] is True
    assert len(r.json()["follow_entries"]) == 0


def test_get_own_following_list_empty(test_db, server_address):
    r = requests.get(f"{server_address}/api/v3/user/following",
                     json={
                         "sort_type": FollowListSortTypes.AGE_DESCENDING.value,
                         "count": 10,
                         "offset": 0
                     },
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200
    assert r.json()["meta"]["count"] == 0
    assert r.json()["meta"]["reached_end"] is True
    assert len(r.json()["follow_entries"]) == 0


def test_get_followers_list_empty(test_db, server_address):
    create_user_with_request(username="user2")
    r = requests.get(f"{server_address}/api/v3/user/followers",
                     json={
                         "sort_type": FollowListSortTypes.AGE_DESCENDING.value,
                         "username": "user2",
                         "count": 10,
                         "offset": 0
                     },
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200
    assert r.json()["meta"]["count"] == 0
    assert r.json()["meta"]["reached_end"] is True
    assert len(r.json()["follow_entries"]) == 0


def test_get_own_followers_list_empty(test_db, server_address):
    r = requests.get(f"{server_address}/api/v3/user/followers",
                     json={
                         "sort_type": FollowListSortTypes.AGE_DESCENDING.value,
                         "count": 10,
                         "offset": 0
                     },
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200
    assert r.json()["meta"]["count"] == 0
    assert r.json()["meta"]["reached_end"] is True
    assert len(r.json()["follow_entries"]) == 0


def test_get_own_following_list(test_db, server_address):
    for user_number in range(1, 21):
        username = f"user{user_number}"
        create_user_with_request(username=username)
        follow_user_with_request(username=username, auth_token=test_db.access_token)

    r = requests.get(f"{server_address}/api/v3/user/following",
                     json={
                         "sort_type": FollowListSortTypes.AGE_DESCENDING.value,
                         "count": 10,
                         "offset": 0
                     },
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200
    assert r.json()["meta"]["count"] == 20
    assert r.json()["meta"]["reached_end"] is False
    assert len(r.json()["follow_entries"]) == 10


def test_get_own_followers_list(test_db, server_address):
    for user_number in range(1, 21):
        username = f"user{user_number}"
        create_user_with_request(username=username, password="password")
        user_access_token = create_user_session_with_request(username=username, password="password")
        follow_user_with_request(username=test_db.username, auth_token=user_access_token)

    r = requests.get(f"{server_address}/api/v3/user/followers",
                     json={
                         "sort_type": FollowListSortTypes.AGE_DESCENDING.value,
                         "count": 10,
                         "offset": 0
                     },
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200
    assert r.json()["meta"]["count"] == 20
    assert r.json()["meta"]["reached_end"] is False
    assert len(r.json()["follow_entries"]) == 10


def test_get_following_list(test_db, server_address):
    create_user_with_request(username="user_that_follows", password="password")
    access_token = create_user_session_with_request(username="user_that_follows", password="password")
    for user_number in range(1, 21):
        username = f"user{user_number}"
        create_user_with_request(username=username)
        follow_user_with_request(username=username, auth_token=access_token)

    r = requests.get(f"{server_address}/api/v3/user/following",
                     json={
                         "username": "user_that_follows",
                         "sort_type": FollowListSortTypes.AGE_DESCENDING.value,
                         "count": 10,
                         "offset": 0
                     },
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200
    assert r.json()["meta"]["count"] == 20
    assert r.json()["meta"]["reached_end"] is False
    assert len(r.json()["follow_entries"]) == 10


def test_get_follower_list(test_db, server_address):
    create_user_with_request(username="user_to_be_followed", password="password")
    for user_number in range(1, 21):
        username = f"user{user_number}"
        create_user_with_request(username=username, password="password")
        access_token = create_user_session_with_request(username=username, password="password")
        follow_user_with_request(username="user_to_be_followed", auth_token=access_token)

    r = requests.get(f"{server_address}/api/v3/user/followers",
                     json={
                         "username": "user_to_be_followed",
                         "sort_type": FollowListSortTypes.AGE_DESCENDING.value,
                         "count": 10,
                         "offset": 0
                     },
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200
    assert r.json()["meta"]["count"] == 20
    assert r.json()["meta"]["reached_end"] is False
    assert len(r.json()["follow_entries"]) == 10
