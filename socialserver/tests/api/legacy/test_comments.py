# noinspection PyUnresolvedReferences
from socialserver.util.test import test_db, server_address, create_user_with_request, create_post_with_request
import requests


def test_create_comment_legacy(test_db, server_address):
    post_id = create_post_with_request(server_address, test_db.access_token,
                                       text_content="post text post text")

    # make a comment
    r = requests.post(f"{server_address}/api/v1/comments",
                      json={
                          "session_token": test_db.access_token,
                          "post_id": post_id,
                          "comment": "the quick brown fox smth smth"
                      })
    assert r.status_code == 201


def test_get_comment_legacy(test_db, server_address):
    comment_text = "the quick brown fox smth smth"
    post_id = create_post_with_request(server_address, test_db.access_token,
                                       text_content="post text post text")

    # make a comment
    r = requests.post(f"{server_address}/api/v1/comments",
                      json={
                          "session_token": test_db.access_token,
                          "post_id": post_id,
                          "comment": comment_text
                      })
    assert r.status_code == 201

    # get the comment (fresh db, so it will always be comment id 1)
    r = requests.get(f"{server_address}/api/v1/comments",
                     json={
                         "session_token": test_db.access_token,
                         "comment_id": 1
                     })

    assert r.status_code == 201
    assert r.json()['username'] == test_db.username
    assert r.json()['comment'] == comment_text


def test_get_comment_feed_legacy(test_db, server_address):
    comment_text = "the quick brown fox smth smth"
    post_id = create_post_with_request(server_address, test_db.access_token,
                                       text_content="post text post text")

    # make a comment
    r = requests.post(f"{server_address}/api/v1/comments",
                      json={
                          "session_token": test_db.access_token,
                          "post_id": post_id,
                          "comment": comment_text
                      })
    assert r.status_code == 201

    # get the comment (fresh db, so it will always be comment id 1)
    r = requests.get(f"{server_address}/api/v1/comments/byPost",
                     json={
                         "session_token": test_db.access_token,
                         "post_id": post_id,
                         "count": 10,
                         "offset": 0
                     })
    assert r.status_code == 201
    assert len(r.json()) == 1
    # 1 will be comment id since it's a blank db
    assert r.json()[0] == 1


def test_get_comment_feed_empty_legacy(test_db, server_address):
    post_id = create_post_with_request(server_address, test_db.access_token,
                                       text_content="post text post text")

    # get the comment (fresh db, so it will always be comment id 1)
    r = requests.get(f"{server_address}/api/v1/comments/byPost",
                     json={
                         "session_token": test_db.access_token,
                         "post_id": post_id,
                         "count": 10,
                         "offset": 0
                     })
    assert r.status_code == 201
    assert len(r.json()) == 0


def test_delete_comment_legacy(test_db, server_address):
    comment_text = "the quick brown fox smth smth"
    post_id = create_post_with_request(server_address, test_db.access_token,
                                       text_content="post text post text")

    # make a comment
    r = requests.post(f"{server_address}/api/v1/comments",
                      json={
                          "session_token": test_db.access_token,
                          "post_id": post_id,
                          "comment": comment_text
                      })
    assert r.status_code == 201

    # get rid of it immediately
    r = requests.delete(f"{server_address}/api/v1/comments",
                        json={
                            "session_token": test_db.access_token,
                            "comment_id": 1
                        })

    assert r.status_code == 201

    # try to get it
    r = requests.get(f"{server_address}/api/v1/comments",
                     json={
                         "session_token": test_db.access_token,
                         "comment_id": 1
                     })

    # weird oddity with the old server code. this is supposed to be 400,
    # not 404!
    assert r.status_code == 400


def test_delete_comment_invalid_id_legacy(test_db, server_address):
    comment_text = "the quick brown fox smth smth"
    post_id = create_post_with_request(server_address, test_db.access_token,
                                       text_content="post text post text")

    # try to remove the non-existent comment
    r = requests.delete(f"{server_address}/api/v1/comments",
                        json={
                            "session_token": test_db.access_token,
                            "comment_id": 1
                        })

    assert r.status_code == 404


def test_like_comment_legacy(test_db, server_address):
    post_id = create_post_with_request(server_address, test_db.access_token,
                                       text_content="post text post text")

    # make a comment
    r = requests.post(f"{server_address}/api/v1/comments",
                      json={
                          "session_token": test_db.access_token,
                          "post_id": post_id,
                          "comment": "the quick brown fox smth smth"
                      })
    assert r.status_code == 201

    # like it oh yes
    r = requests.post(f"{server_address}/api/v2/comments/like",
                      json={
                          "session_token": test_db.access_token,
                          "comment_id": 1
                      })
    assert r.status_code == 201
    assert r.json()['commentLiked'] is True

    # get the comment like count, just to make sure!
    r = requests.get(f"{server_address}/api/v1/comments",
                     json={
                         "session_token": test_db.access_token,
                         "comment_id": 1
                     })

    assert r.json()['likeCount'] == 1


def test_unlike_comment_legacy(test_db, server_address):
    post_id = create_post_with_request(server_address, test_db.access_token,
                                       text_content="post text post text")

    # make a comment
    r = requests.post(f"{server_address}/api/v1/comments",
                      json={
                          "session_token": test_db.access_token,
                          "post_id": post_id,
                          "comment": "the quick brown fox smth smth"
                      })
    assert r.status_code == 201

    # like it oh yes
    r = requests.post(f"{server_address}/api/v2/comments/like",
                      json={
                          "session_token": test_db.access_token,
                          "comment_id": 1
                      })
    assert r.status_code == 201
    assert r.json()['commentLiked'] is True

    # i do not like it anymore :(
    r = requests.post(f"{server_address}/api/v2/comments/like",
                      json={
                          "session_token": test_db.access_token,
                          "comment_id": 1
                      })
    assert r.status_code == 201
    assert r.json()['commentLiked'] is False

    # get the comment like count, just to make sure!
    r = requests.get(f"{server_address}/api/v1/comments",
                     json={
                         "session_token": test_db.access_token,
                         "comment_id": 1
                     })

    assert r.json()['likeCount'] == 0
