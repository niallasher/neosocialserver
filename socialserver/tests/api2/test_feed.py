# noinspection PyUnresolvedReferences
from socialserver.util.test import test_db, server_address, create_post_with_request, create_user_with_request, \
    create_user_session_with_request
from socialserver.constants import ErrorCodes, MAX_FEED_GET_COUNT
import requests


def test_get_all_feed_no_posts(test_db, server_address):
    r = requests.get(f'{server_address}/api/v2/feed/posts',
                     json={
                         "access_token": test_db.access_token,
                         "count": 15,
                         "offset": 0,
                     })
    assert r.status_code == 201
    assert r.json()['meta']['reached_end'] == True
    assert len(r.json()['posts']) == 0


def test_get_all_feed_less_than_count_posts(test_db, server_address):
    # range excludes last number, so this is actually 14.
    for i in range(1, 15):
        create_post_with_request(server_address,
                                 test_db.access_token)
    r = requests.get(f'{server_address}/api/v2/feed/posts',
                     json={
                         "access_token": test_db.access_token,
                         "count": 15,
                         "offset": 0
                     })
    assert r.status_code == 201
    assert r.json()['meta']['reached_end'] == True
    assert len(r.json()['posts']) == 14


def test_get_all_feed_more_than_count_posts(test_db, server_address):
    for i in range(1, 30):
        create_post_with_request(server_address,
                                 test_db.access_token)

    r = requests.get(f'{server_address}/api/v2/feed/posts',
                     json={
                         "access_token": test_db.access_token,
                         "count": 15,
                         "offset": 0
                     })

    assert r.status_code == 201
    assert r.json()['meta']['reached_end'] == False
    assert len(r.json()['posts']) == 15


def test_get_posts_from_specific_usernames(test_db, server_address):
    # create a post from user test, so we can check if it's been
    # filtered ok later
    create_post_with_request(server_address, test_db.access_token)
    create_user_with_request(server_address, username="user1", password="password", display_name="user1")
    create_user_with_request(server_address, username="user2", password="password", display_name="user2")
    at_user_one = create_user_session_with_request(server_address, username="user1", password="password")
    at_user_two = create_user_session_with_request(server_address, username="user2", password="password")

    create_post_with_request(server_address, auth_token=at_user_one)
    create_post_with_request(server_address, auth_token=at_user_two)

    r = requests.get(f"{server_address}/api/v2/feed/posts",
                     json={
                         "access_token": test_db.access_token,
                         "count": 15,
                         "offset": 0,
                         "username": ["user1", "user2"]
                     })

    print(r.json())
    assert r.status_code == 201
    assert len(r.json()['posts']) == 2
