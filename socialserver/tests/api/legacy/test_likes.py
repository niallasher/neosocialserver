# noinspection PyUnresolvedReferences
from socialserver.util.test import test_db, create_post_with_request, create_user_with_request, \
    create_user_session_with_request, server_address
import requests


def test_like_post_legacy(test_db, server_address):
    post_id = create_post_with_request(server_address, test_db.access_token)
    r = requests.post(f"{server_address}/api/v1/likes",
                      json={
                          "session_token": test_db.access_token,
                          "post_id": post_id
                      })
    assert r.status_code == 201
    assert r.json()['postIsLiked'] is True


def test_like_post_invalid_id_legacy(test_db, server_address):
    r = requests.post(f"{server_address}/api/v1/likes",
                      json={
                          "session_token": test_db.access_token,
                          "post_id": 33
                      })
    assert r.status_code == 404


def test_unlike_post_legacy(test_db, server_address):
    post_id = create_post_with_request(server_address, test_db.access_token)
    # create a like first, since we need one to delete one :)
    requests.post(f"{server_address}/api/v1/likes",
                  json={
                      "session_token": test_db.access_token,
                      "post_id": post_id
                  })
    r = requests.post(f"{server_address}/api/v1/likes",
                      json={
                          "session_token": test_db.access_token,
                          "post_id": post_id
                      })
    assert r.status_code == 201
    assert r.json()['postIsLiked'] is False

    # not much point in yet another test for unlike with invalid id; it's the exact same
    # endpoint anyway!


def test_get_like_count_no_likes_legacy(test_db, server_address):
    post_id = create_post_with_request(server_address, test_db.access_token)
    r = requests.get(f"{server_address}/api/v1/likes/byPost",
                     json={
                         "session_token": test_db.access_token,
                         "post_id": post_id,
                         "count": 10,
                         "offset": 0
                     })
    assert r.status_code == 201
    assert len(r.json()) == 0


def test_get_like_count_legacy(test_db, server_address):
    post_id = create_post_with_request(server_address, test_db.access_token)
    r = requests.post(f"{server_address}/api/v1/likes",
                      json={
                          "session_token": test_db.access_token,
                          "post_id": post_id
                      })
    r = requests.get(f"{server_address}/api/v1/likes/byPost",
                     json={
                         "session_token": test_db.access_token,
                         "post_id": post_id,
                         "count": 10,
                         "offset": 0
                     })
    assert r.status_code == 201
    assert len(r.json()) == 1


def test_get_like_info_legacy(test_db, server_address):
    post_id = create_post_with_request(server_address, test_db.access_token)
    # like the post
    requests.post(f"{server_address}/api/v1/likes",
                  json={
                      "session_token": test_db.access_token,
                      "post_id": post_id
                  })
    # get the id of that like
    like_id = requests.get(f"{server_address}/api/v1/likes/byPost",
                           json={
                               "session_token": test_db.access_token,
                               "post_id": post_id,
                               "count": 10,
                               "offset": 0
                           }).json()[0]
    # and finally get the info
    r = requests.get(f"{server_address}/api/v1/likes",
                     json={
                         "session_token": test_db.access_token,
                         "like_id": like_id
                     })
    assert r.status_code == 201
    assert r.json()['username'] == test_db.username


def test_get_like_info_invalid_id_legacy(test_db, server_address):
    r = requests.get(f"{server_address}/api/v1/likes",
                     json={
                         "session_token": test_db.access_token,
                         "like_id": 1337
                     })
    assert r.status_code == 404
