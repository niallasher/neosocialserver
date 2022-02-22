#  Copyright (c) Niall Asher 2022

from socialserver.util.test import test_db, server_address, create_user_with_request, \
    create_user_session_with_request, create_comment_with_request, create_post_with_request
import requests
from socialserver.constants import ErrorCodes


def test_like_comment(test_db, server_address):
    post_id = create_post_with_request(server_address, test_db.access_token)
    comment_id = create_comment_with_request(test_db.access_token, post_id)

    r = requests.post(f"{server_address}/api/v3/comments/like",
                      json={
                          "comment_id": comment_id
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 201
    assert r.json()['liked'] is True
    assert r.json()['like_count'] == 1


def test_like_comment_already_liked(test_db, server_address):
    post_id = create_post_with_request(server_address, test_db.access_token)
    comment_id = create_comment_with_request(test_db.access_token, post_id)

    r = requests.post(f"{server_address}/api/v3/comments/like",
                      json={
                          "comment_id": comment_id
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 201
    assert r.json()['liked'] is True
    assert r.json()['like_count'] == 1

    r = requests.post(f"{server_address}/api/v3/comments/like",
                      json={
                          "comment_id": comment_id
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 400
    assert r.json()['error'] == ErrorCodes.OBJECT_ALREADY_LIKED.value


def test_unlike_comment(test_db, server_address):
    post_id = create_post_with_request(server_address, test_db.access_token)
    comment_id = create_comment_with_request(test_db.access_token, post_id)

    r = requests.post(f"{server_address}/api/v3/comments/like",
                      json={
                          "comment_id": comment_id
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 201
    assert r.json()['liked'] is True
    assert r.json()['like_count'] == 1

    r = requests.delete(f"{server_address}/api/v3/comments/like",
                        json={
                            "comment_id": comment_id
                        },
                        headers={
                            "Authorization": f"bearer {test_db.access_token}"
                        })

    assert r.status_code == 200
    assert r.json()['liked'] is False
    assert r.json()['like_count'] == 0


def test_unlike_comment_not_liked(test_db, server_address):
    post_id = create_post_with_request(server_address, test_db.access_token)
    comment_id = create_comment_with_request(test_db.access_token, post_id)

    r = requests.delete(f"{server_address}/api/v3/comments/like",
                        json={
                            "comment_id": comment_id
                        },
                        headers={
                            "Authorization": f"bearer {test_db.access_token}"
                        })

    assert r.status_code == 400
    assert r.json()['error'] == ErrorCodes.OBJECT_NOT_LIKED.value


def test_like_comment_invalid_id(test_db, server_address):
    r = requests.post(f"{server_address}/api/v3/comments/like",
                      json={
                          "comment_id": 420
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })

    assert r.status_code == 404
    assert r.json()['error'] == ErrorCodes.COMMENT_NOT_FOUND.value


def test_unlike_comment_invalid_id(test_db, server_address):
    r = requests.delete(f"{server_address}/api/v3/comments/like",
                        json={
                            "comment_id": 420
                        },
                        headers={
                            "Authorization": f"bearer {test_db.access_token}"
                        })

    assert r.status_code == 404
    assert r.json()['error'] == ErrorCodes.COMMENT_NOT_FOUND.value
