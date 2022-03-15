#  Copyright (c) Niall Asher 2022

# disabling PyUnresolvedReferences for the import.
# noinspection PyUnresolvedReferences
from socialserver.util.test import (
    create_comment_with_request,
    create_user_with_request,
    server_address,
    test_db,
    create_post_with_request,
)
from socialserver.constants import CommentFeedSortTypes, ErrorCodes
import requests


# TODO: Like sort testing will need to be implemented when comment likes are!


def test_get_comment_feed_empty(server_address, test_db):
    post_id = create_post_with_request(test_db.access_token)
    r = requests.get(
        f"{server_address}/api/v3/comments/feed",
        json={
            "count": 10,
            "offset": 0,
            "sort": CommentFeedSortTypes.CREATION_TIME_DESCENDING.value,
            "post_id": post_id,
        },
        headers={"Authorization": f"bearer {test_db.access_token}"},
    )

    assert r.status_code == 200
    assert len(r.json()["comments"]) == 0
    assert r.json()["meta"]["reached_end"] is True


def test_get_comment_feed(server_address, test_db):
    post_id = create_post_with_request(test_db.access_token)
    comment_count = 15
    for i in range(0, comment_count):
        create_comment_with_request(test_db.access_token, post_id)

    r = requests.get(
        f"{server_address}/api/v3/comments/feed",
        json={
            "count": 10,
            "offset": 0,
            "sort": CommentFeedSortTypes.CREATION_TIME_DESCENDING.value,
            "post_id": post_id,
        },
        headers={"Authorization": f"bearer {test_db.access_token}"},
    )

    assert r.status_code == 200
    assert r.json()["meta"]["reached_end"] is False
    assert len(r.json()["comments"]) == 10


def test_get_comment_feed_count_higher_than_comment_count(server_address, test_db):
    post_id = create_post_with_request(test_db.access_token)
    comment_count = 15
    for i in range(0, comment_count):
        create_comment_with_request(test_db.access_token, post_id)

    r = requests.get(
        f"{server_address}/api/v3/comments/feed",
        json={
            "count": 20,
            "offset": 0,
            "sort": CommentFeedSortTypes.CREATION_TIME_DESCENDING.value,
            "post_id": post_id,
        },
        headers={"Authorization": f"bearer {test_db.access_token}"},
    )

    assert r.status_code == 200
    assert r.json()["meta"]["reached_end"] is True
    assert len(r.json()["comments"]) == 15


def test_get_comment_feed_invalid_post_id(server_address, test_db):
    r = requests.get(
        f"{server_address}/api/v3/comments/feed",
        json={
            "count": 10,
            "offset": 0,
            "sort": CommentFeedSortTypes.CREATION_TIME_DESCENDING.value,
            "post_id": 1337,
        },
        headers={"Authorization": f"bearer {test_db.access_token}"},
    )
    assert r.status_code == 404
    assert r.json()["error"] == ErrorCodes.POST_NOT_FOUND.value
