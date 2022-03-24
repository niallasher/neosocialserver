#  Copyright (c) Niall Asher 2022, PostAdditionalContentTypes

# noinspection PyUnresolvedReferences
from socialserver.util.test import (
    test_db,
    server_address,
    create_post_with_request,
    create_user_with_request,
    create_user_session_with_request,
    image_data_binary,
)
from socialserver.constants import ErrorCodes
import requests


def test_create_single_post(test_db, server_address, monkeypatch):
    r = requests.post(
        f"{server_address}/api/v3/posts/single",
        json={"text_content": "Test Post"},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    print(r.json())
    assert r.status_code == 200
    # blank database, so this should be post id 1.
    assert r.json()["post_id"] == 1


def test_create_single_post_unprocessed_image(
    test_db, server_address, image_data_binary
):
    r = requests.post(
        f"{server_address}/api/v3/image",
        files={"image": image_data_binary},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )
    assert r.status_code == 201
    assert r.json()["processed"] is False
    identifier = r.json()["identifier"]

    # on the off change you have a genuinely absurdly powerful
    # system, you might fail this test if the image uploads in like 3ms :)
    r = requests.post(
        f"{server_address}/api/v3/posts/single",
        json={"text_content": "Test Post", "images": [identifier]},
        headers={"Authorization": f"bearer {test_db.access_token}"},
    )
    print(r.text)
    assert r.status_code == 200
    assert r.json()["processed"] is False


def test_create_single_post_missing_args(test_db, server_address, monkeypatch):
    r = requests.post(
        f"{server_address}/api/v3/posts/single",
        json={},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    assert r.status_code == 400


def test_create_single_post_invalid_access_token(test_db, server_address, monkeypatch):
    r = requests.post(
        f"{server_address}/api/v3/posts/single",
        json={"text_content": "Test Post"},
        headers={"Authorization": f"Bearer invalid"},
    )

    assert r.status_code == 401
    assert r.json()["error"] == ErrorCodes.TOKEN_INVALID.value


def test_get_single_post(test_db, server_address, monkeypatch):
    new_post_id = create_post_with_request(test_db.access_token)

    r = requests.get(
        f"{server_address}/api/v3/posts/single",
        json={"post_id": new_post_id},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    assert r.status_code == 201
    assert r.json()["post"]["id"] == new_post_id
    assert r.json()["user"]["username"] == test_db.username


def test_get_single_post_not_exist(test_db, server_address, monkeypatch):
    r = requests.get(
        f"{server_address}/api/v3/posts/single",
        json={
            # we're on a blank database. 1 shouldn't exist.
            "post_id": 1
        },
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    assert r.status_code == 404
    assert r.json()["error"] == ErrorCodes.POST_NOT_FOUND.value


def test_get_single_post_unprocessed(test_db, server_address, monkeypatch):
    r = requests.get(
        f"{server_address}/api/v3/posts/single",
        json={
            # we're on a blank database. 1 shouldn't exist.
            "post_id": 1
        },
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    assert r.status_code == 404
    assert r.json()["error"] == ErrorCodes.POST_NOT_FOUND.value


def test_get_single_post_invalid_access_token(test_db, server_address, monkeypatch):
    new_post_id = create_post_with_request(test_db.access_token)

    r = requests.get(
        f"{server_address}/api/v3/posts/single",
        json={"post_id": new_post_id},
        headers={"Authorization": f"Bearer invalid"},
    )

    assert r.status_code == 401
    assert r.json()["error"] == ErrorCodes.TOKEN_INVALID.value


def test_get_single_post_missing_args(test_db, server_address, monkeypatch):
    create_post_with_request(test_db.access_token)

    r = requests.get(
        f"{server_address}/api/v3/posts/single",
        json={},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    assert r.status_code == 400


def test_delete_post(test_db, server_address, monkeypatch):
    post_id = create_post_with_request(test_db.access_token)

    r = requests.delete(
        f"{server_address}/api/v3/posts/single",
        json={"post_id": post_id},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    assert r.status_code == 200


def test_delete_post_invalid_id(test_db, server_address, monkeypatch):
    post_id = create_post_with_request(test_db.access_token)

    r = requests.delete(
        f"{server_address}/api/v3/posts/single",
        json={"post_id": 1371219381},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    assert r.status_code == 404
    assert r.json()["error"] == ErrorCodes.POST_NOT_FOUND.value


def test_try_delete_post_from_other_user(test_db, server_address, monkeypatch):
    create_user_with_request("user2", "password")
    access_token = create_user_session_with_request("user2", "password")
    # create post using the second account
    post_id = create_post_with_request(access_token)

    # and try to delete using the first one
    r = requests.delete(
        f"{server_address}/api/v3/posts/single",
        json={"post_id": post_id},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    assert r.status_code == 401
    assert r.json()["error"] == ErrorCodes.OBJECT_NOT_OWNED_BY_USER.value
