#  Copyright (c) Niall Asher 2022

from socialserver.util.test import (
    test_db,
    server_address,
    create_post_with_request,
    create_user_with_request,
    create_user_session_with_request
)
from socialserver.constants import ErrorCodes
import requests

def test_get_unliked_post(test_db, server_address):
    new_post_id = create_post_with_request(test_db.access_token)
    r = requests.get(
        f"{server_address}/api/v3/posts/single",
        json={"post_id": new_post_id},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )
    assert r.status_code == 201
    assert r.json()['meta']['user_likes_post'] == False
    assert r.json()['post']['like_count'] == 0

def test_like_post(test_db, server_address):
    new_post_id = create_post_with_request(test_db.access_token)
    r = requests.post(f"{server_address}/api/v3/posts/like",
                      json={"post_id": new_post_id},
                      headers={"Authorization": f"Bearer {test_db.access_token}"})
    assert r.status_code == 201
    assert r.json()['liked'] == True
    assert r.json()['like_count'] == 1
    r = requests.get(
        f"{server_address}/api/v3/posts/single",
        json={"post_id": new_post_id},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )
    assert r.status_code == 201
    assert r.json()['meta']['user_likes_post'] == True
    assert r.json()['post']['like_count'] == 1

def test_unlike_post(test_db, server_address):
    new_post_id = create_post_with_request(test_db.access_token)
    r = requests.post(f"{server_address}/api/v3/posts/like",
                      json={"post_id": new_post_id},
                      headers={"Authorization": f"Bearer {test_db.access_token}"})
    assert r.status_code == 201
    assert r.json()['liked'] == True
    assert r.json()['like_count'] == 1
    r = requests.delete(
        f"{server_address}/api/v3/posts/like",
        json={"post_id": new_post_id},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )
    assert r.status_code == 200
    assert r.json()['liked'] == False
    assert r.json()['like_count'] == 0

def test_like_post_already_liked(test_db, server_address):
    new_post_id = create_post_with_request(test_db.access_token)
    r = requests.post(f"{server_address}/api/v3/posts/like",
                      json={"post_id": new_post_id},
                      headers={"Authorization": f"Bearer {test_db.access_token}"})
    assert r.status_code == 201
    assert r.json()['liked'] == True
    assert r.json()['like_count'] == 1
    r2 = requests.post(f"{server_address}/api/v3/posts/like",
                      json={"post_id": new_post_id},
                      headers={"Authorization": f"Bearer {test_db.access_token}"})
    assert r2.status_code == 400
    assert r2.json()["error"] == ErrorCodes.OBJECT_ALREADY_LIKED.value


def test_unlike_post_not_liked(test_db, server_address):
    new_post_id = create_post_with_request(test_db.access_token)
    r = requests.delete(f"{server_address}/api/v3/posts/like",
                      json={"post_id": new_post_id},
                      headers={"Authorization": f"Bearer {test_db.access_token}"})
    assert r.status_code == 400
    assert r.json()["error"] == ErrorCodes.OBJECT_NOT_LIKED.value


def test_like_post_does_not_exist(test_db, server_address):
    r = requests.post(f"{server_address}/api/v3/posts/like",
                      json={"post_id": 1293812},
                      headers={"Authorization": f"Bearer {test_db.access_token}"})
    assert r.status_code == 404
    assert r.json()["error"] == ErrorCodes.POST_NOT_FOUND.value


def test_dislike_post_does_not_exist(test_db, server_address):
    r = requests.delete(f"{server_address}/api/v3/posts/like",
                      json={"post_id": 1293812},
                      headers={"Authorization": f"Bearer {test_db.access_token}"})
    assert r.status_code == 404
    assert r.json()["error"] == ErrorCodes.POST_NOT_FOUND.value
