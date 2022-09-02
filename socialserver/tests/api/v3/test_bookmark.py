#  Copyright (c) Niall Asher 2022
from socialserver.util.test import test_db, server_address, create_user_with_request, create_post_with_request, \
    create_user_session_with_request
from socialserver.constants import ErrorCodes
import requests


def test_bookmark_post(test_db, server_address, monkeypatch):
    # post to bookmark
    post_id = create_post_with_request(test_db.access_token)
    # bookmark it
    r = requests.post(f"{server_address}/api/v3/posts/bookmark",
                      json={
                          "post_id": post_id
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 200
    assert r.json()["post_bookmarked"] is True
    # now un-bookmark it
    r2 = requests.delete(f"{server_address}/api/v3/posts/bookmark",
                         json={
                             "post_id": post_id
                         },
                         headers={
                             "Authorization": f"bearer {test_db.access_token}"
                         })
    assert r2.status_code == 200
    assert r2.json()["post_bookmarked"] is False


def test_bookmark_post_attempt_double_bookmark(test_db, server_address, monkeypatch):
    # post to bookmark
    post_id = create_post_with_request(test_db.access_token)
    # bookmark it
    r = requests.post(f"{server_address}/api/v3/posts/bookmark",
                      json={
                          "post_id": post_id
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 200
    assert r.json()["post_bookmarked"] is True
    # now try to bookmark again
    r2 = requests.post(f"{server_address}/api/v3/posts/bookmark",
                       json={
                           "post_id": post_id
                       },
                       headers={
                           "Authorization": f"bearer {test_db.access_token}"
                       })
    assert r2.status_code == 400
    assert r2.json()["error"] == ErrorCodes.POST_ALREADY_BOOKMARKED.value


def test_bookmark_remove_non_existent_bookmark(test_db, server_address, monkeypatch):
    # post to (not) bookmark
    post_id = create_post_with_request(test_db.access_token)
    # try to delete its bookmark, even though it doesn't exist.
    # what could go wrong?
    r = requests.delete(f"{server_address}/api/v3/posts/bookmark",
                        json={
                            "post_id": post_id
                        },
                        headers={
                            "Authorization": f"bearer {test_db.access_token}"
                        })
    assert r.status_code == 400
    assert r.json()["error"] == ErrorCodes.POST_NOT_BOOKMARKED.value


def test_bookmark_feed(test_db, server_address, monkeypatch):
    for i in range(0, 15):
        post_id = create_post_with_request(test_db.access_token, text_content="test post for bookmark feed")
        r = requests.post(f"{server_address}/api/v3/posts/bookmark",
                          json={
                              "post_id": post_id
                          },
                          headers={
                              "Authorization": f"bearer {test_db.access_token}"
                          })
        assert r.status_code == 200
    r = requests.get(f"{server_address}/api/v3/posts/bookmark/feed",
                     json={
                         "count": 10,
                         "offset": 0
                     },
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 201
    assert r.json()["meta"]["reached_end"] is False
    assert len(r.json()["posts"]) == 10  # same as count ofc.


def test_bookmark_feed_empty(test_db, server_address, monkeypatch):
    r = requests.get(f"{server_address}/api/v3/posts/bookmark/feed",
                     json={
                         "count": 10,
                         "offset": 0
                     },
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 201
    assert r.json()["meta"]["reached_end"] is True
    assert len(r.json()["posts"]) == 0
