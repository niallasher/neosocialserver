#  Copyright (c) Niall Asher 2022

# noinspection PyUnresolvedReferences
from socialserver.util.test import test_db, server_address, create_post_with_request
from socialserver.constants import ErrorCodes, CommentFeedSortTypes, COMMENT_MAX_LEN
import requests


def test_post_comment(test_db, server_address):
    comment_text = "i'm a comment look at me"

    post_id = create_post_with_request(test_db.access_token)
    r = requests.post(
        f"{server_address}/api/v3/comments",
        json={"post_id": post_id, "text_content": comment_text},
        headers={"Authorization": f"bearer {test_db.access_token}"},
    )
    assert r.status_code == 201

    # check it's there
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
    assert len(r.json()["comments"]) == 1


def test_post_comment_too_long(test_db, server_address):
    post_id = create_post_with_request(test_db.access_token)
    r = requests.post(
        f"{server_address}/api/v3/comments",
        json={"post_id": post_id, "text_content": "a" * (COMMENT_MAX_LEN + 1)},
        headers={"Authorization": f"bearer {test_db.access_token}"},
    )
    assert r.status_code == 400
    assert r.json()["error"] == ErrorCodes.COMMENT_TOO_LONG.value

    # check it's there
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


def test_post_comment_too_short(test_db, server_address):
    post_id = create_post_with_request(test_db.access_token)
    r = requests.post(
        f"{server_address}/api/v3/comments",
        json={"post_id": post_id, "text_content": ""},
        headers={"Authorization": f"bearer {test_db.access_token}"},
    )
    assert r.status_code == 400
    assert r.json()["error"] == ErrorCodes.COMMENT_TOO_SHORT.value

    # check it's there
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


def test_delete_comment(test_db, server_address):
    comment_text = "i'm a comment look at me"

    # make the comment
    post_id = create_post_with_request(test_db.access_token)
    r = requests.post(
        f"{server_address}/api/v3/comments",
        json={"post_id": post_id, "text_content": comment_text},
        headers={"Authorization": f"bearer {test_db.access_token}"},
    )
    assert r.status_code == 201

    comment_id = r.json()["id"]

    # check it's there
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
    assert len(r.json()["comments"]) == 1

    # nuke from orbit

    r = requests.delete(
        f"{server_address}/api/v3/comments",
        json={"comment_id": comment_id},
        headers={"Authorization": f"bearer {test_db.access_token}"},
    )

    assert r.status_code == 200

    # check it's well and truly decimated
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
