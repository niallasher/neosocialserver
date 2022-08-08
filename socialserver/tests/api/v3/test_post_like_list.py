#  Copyright (c) Niall Asher 2022
import random
import string
from secrets import token_urlsafe

from socialserver.util.test import (
    test_db,
    server_address,
    create_post_with_request,
    create_user_with_request,
    create_user_session_with_request
)
from socialserver.constants import ErrorCodes, MAX_FEED_GET_COUNT
import requests


def test_post_like_list_no_likes(test_db, server_address):
    new_post_id = create_post_with_request(test_db.access_token)
    r = requests.get(f"{server_address}/api/v3/posts/like/feed",
                     json={"post_id": new_post_id, "count": 10, "offset": 0},
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    print(r.json())
    assert r.json()["meta"]["count"] == 0
    assert r.json()["meta"]["reached_end"] == True
    assert len(r.json()["like_entries"]) == 0


def test_post_like_list(test_db, server_address):
    new_post_id = create_post_with_request(test_db.access_token)

    # like the post 15 times
    for i in range(0, 15):
        letters = string.ascii_lowercase
        new_username = ''.join(random.choice(letters) for i in range(15))

        create_user_with_request(username=new_username)
        token = create_user_session_with_request(username=new_username, password="password")

        nr = requests.post(f"{server_address}/api/v3/posts/like",
                           json={
                               "post_id": new_post_id
                           },
                           headers={
                               "Authorization": f"bearer {token}"
                           })

        assert nr.status_code == 201

    r = requests.get(f"{server_address}/api/v3/posts/like/feed",
                     json={
                         "post_id": new_post_id,
                         "count": 10,
                         "offset": 0
                     },
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })

    assert r.status_code == 200
    print(f"\n\n\n\n {r.json()} \n\n\n\n")
    assert r.json()["meta"]["reached_end"] is False
    assert r.json()["meta"]["count"] == 15
    assert len(r.json()["like_entries"]) == 10


def test_post_like_list_invalid_post(test_db, server_address):
    r = requests.get(f"{server_address}/api/v3/posts/like/feed",
                     json={
                         "post_id": 1239831,
                         "count": 10,
                         "offset": 0
                     },
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 404
    assert r.json()["error"] == ErrorCodes.POST_NOT_FOUND.value


def test_post_like_list_get_count_too_high(test_db, server_address):
    new_post_id = create_post_with_request(test_db.access_token)
    r = requests.get(f"{server_address}/api/v3/posts/like/feed",
                     json={
                         "post_id": new_post_id,
                         "count": MAX_FEED_GET_COUNT + 1,
                         "offset": 0
                     },
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 400
    assert r.json()["error"] == ErrorCodes.FEED_GET_COUNT_TOO_HIGH.value
