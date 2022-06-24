#  Copyright (c) Niall Asher 2022

import re
import pony.orm
import pytest
import requests
from os import getenv
from socialserver.db import create_test_db
from pony.orm import db_session
from socialserver.tests.test_data.test_image import TEST_IMAGE_B64
from socialserver.util.namespace import dict_to_simple_namespace
from socialserver.constants import ROOT_DIR
from base64 import urlsafe_b64decode
from io import BytesIO
from fs.memoryfs import MemoryFS

UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 "
    "Mobile/15A372 Safari/604.1 "
)

"""
    test_db
    pytest fixture that creates an in-memory database with a pre-made user account
    and session.
"""


@pytest.fixture
def test_db(monkeypatch):
    test_db = create_test_db()
    monkeypatch_api_db(pytest.MonkeyPatch(), test_db)
    create_user_with_request(username="test", password="password", display_name="test")
    access_token = create_user_session_with_request(
        username="test", password="password"
    )
    return dict_to_simple_namespace(
        {
            "db": test_db,
            "username": "test",
            "password": "password",
            "display_name": "test",
            "access_token": access_token,
        }
    )


"""
    set_user_attributes_db
    set a users attributes via a database object, allowing for creation
    of admins in a test.
"""


@db_session
def set_user_attributes_db(db: pony.orm.Database, username: str, attributes: list):
    user = db.User.get(username=username)
    if user is None:
        raise ValueError
    user.account_attributes = attributes


"""
    server_address
    returns the url of the testing server,
    for tests that need to make requests to it
"""


@pytest.fixture
def server_address():
    return get_server_address()


"""
    image_data_url
    returns a test image data url
"""


@pytest.fixture
def image_data_url():
    return TEST_IMAGE_B64


"""
    image_data_binary
    returns a test image (binary data)
"""


@pytest.fixture
def image_data_binary():
    data_url = TEST_IMAGE_B64
    data_url = re.sub(r"^data:image/.+;base64,", "", data_url)
    buffer = BytesIO(urlsafe_b64decode(data_url))
    return buffer.read()


"""
    video_data_binary
    returns a test video (binary data)
"""


@pytest.fixture
def video_data_binary():
    with open(f"{ROOT_DIR}/tests/test_data/test_video.mp4", "rb") as video_file:
        return video_file.read()


"""
    get_server_address
    
    returns an server address for the testing server,
    respecting the set environment variables
"""


def get_server_address():
    addr = getenv("SOCIALSERVER_TEST_SERVER_ADDRESS", default=None)
    port = getenv("SOCIALSERVER_TEST_SERVER_PORT", default=None)

    return f"http://{'127.0.0.1' if addr is None else addr}:{'9801' if port is None else port}"


"""
    monkey_patch_api_db
    
    uses monkey-patching to replace the db object across
    all api endpoints with the given one, so that tests
    can have a blank database to work with.
"""


def monkeypatch_api_db(monkeypatch: pytest.MonkeyPatch, db: pony.orm.Database) -> None:
    # swap in memory filesystems for video & images, since we only want
    # temporary storage of test media
    temp_image_fs = MemoryFS()
    temp_video_fs = MemoryFS()

    monkeypatch.setattr("socialserver.util.image.fs_images", temp_image_fs)
    monkeypatch.setattr("socialserver.api.v3.image.fs_images", temp_image_fs)

    monkeypatch.setattr("socialserver.util.video.fs_videos", temp_video_fs)
    monkeypatch.setattr("socialserver.api.v3.video.fs_videos", temp_video_fs)

    monkeypatch.setattr("socialserver.util.auth.db", db)
    monkeypatch.setattr("socialserver.util.image.db", db)
    monkeypatch.setattr("socialserver.util.video.db", db)
    monkeypatch.setattr("socialserver.api.v3.block.db", db)
    monkeypatch.setattr("socialserver.api.v3.feed.db", db)
    monkeypatch.setattr("socialserver.api.v3.follow.db", db)
    monkeypatch.setattr("socialserver.api.v3.follow_list.db", db)
    monkeypatch.setattr("socialserver.api.v3.image.db", db)
    monkeypatch.setattr("socialserver.api.v3.post.db", db)
    monkeypatch.setattr("socialserver.api.v3.post_like.db", db)
    monkeypatch.setattr("socialserver.api.v3.report.db", db)
    monkeypatch.setattr("socialserver.api.v3.user.db", db)
    monkeypatch.setattr("socialserver.api.v3.two_factor.db", db)
    monkeypatch.setattr("socialserver.api.v3.user_session.db", db)
    monkeypatch.setattr("socialserver.api.v3.username_available.db", db)
    monkeypatch.setattr("socialserver.api.v3.admin.user_approvals.db", db)
    monkeypatch.setattr("socialserver.api.v3.comment.db", db)
    monkeypatch.setattr("socialserver.api.v3.comment_feed.db", db)
    monkeypatch.setattr("socialserver.api.v3.comment_like.db", db)
    monkeypatch.setattr("socialserver.api.v3.video.db", db)
    # legacy api
    monkeypatch.setattr("socialserver.api.legacy.user.db", db)
    monkeypatch.setattr("socialserver.api.legacy.comment_filter.filter_by_post.db", db)
    monkeypatch.setattr("socialserver.api.legacy.usermod.db", db)
    monkeypatch.setattr("socialserver.api.legacy.authentication.db", db)
    monkeypatch.setattr("socialserver.api.legacy.post_filter.by_user.db", db)
    monkeypatch.setattr("socialserver.api.legacy.post.db", db)
    monkeypatch.setattr("socialserver.api.legacy.modqueue.db", db)
    monkeypatch.setattr("socialserver.api.legacy.like_filter.by_post.db", db)
    monkeypatch.setattr("socialserver.api.legacy.like.db", db)
    monkeypatch.setattr("socialserver.api.legacy.follows.db", db)
    monkeypatch.setattr("socialserver.api.legacy.follower_list.db", db)
    monkeypatch.setattr("socialserver.api.legacy.comment.db", db)
    monkeypatch.setattr("socialserver.api.legacy.block.db", db)
    monkeypatch.setattr("socialserver.api.legacy.two_factor.db", db)
    monkeypatch.setattr("socialserver.api.legacy.bio.db", db)
    monkeypatch.setattr(
        "socialserver.api.legacy.privileged_ops.admin_delete_user.db", db
    )
    monkeypatch.setattr(
        "socialserver.api.legacy.privileged_ops.admin_delete_post.db", db
    )
    monkeypatch.setattr("socialserver.api.legacy.privileged_ops.admin_usermod.db", db)
    return None


"""
    create_comment_with_request
    
    creates a comment on a given postID via API v3
"""


def create_comment_with_request(
    access_token: str, post_id: int, text_content="comment"
):
    server_address = get_server_address()
    r = requests.post(
        f"{server_address}/api/v3/comments",
        json={"post_id": post_id, "text_content": text_content},
        headers={"Authorization": f"bearer {access_token}"},
    )
    assert r.status_code == 201
    return r.json()["id"]


"""
    create_user_with_request
    
    fires a request to server_address, to create a new user
"""


def create_user_with_request(
    username="username", password="password", display_name="name"
):
    server_address = get_server_address()
    r = requests.post(
        f"{server_address}/api/v3/user",
        json={"display_name": display_name, "username": username, "password": password},
    )
    # we want to fail if this didn't work, since tests
    # will fail in strange ways if the account they
    # expect isn't made
    assert r.status_code == 201
    return r.json()


"""
    create_user_session_with_request
    
    takes username & password, and creates a user session
    returns the token.
"""


def create_user_session_with_request(username: str, password: str):
    server_address = get_server_address()
    r = requests.post(
        f"{server_address}/api/v3/user/session",
        json={"username": username, "password": password},
    )

    # fail immediately if it didn't work
    assert r.status_code == 200
    return r.json()["access_token"]


"""
    create_post_with_request
    
    creates a simple post using requests, to test feeds and the like.
    requires user auth token. doesn't support images
"""


def create_post_with_request(auth_token, text_content="Test Post"):
    server_address = get_server_address()
    r = requests.post(
        f"{server_address}/api/v3/posts/single",
        json={"text_content": text_content},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert r.status_code == 200
    return r.json()["post_id"]


"""
    follow_user_with_request
    
    follows a user account using the local api
"""


def follow_user_with_request(auth_token: str, username: str):
    server_address = get_server_address()
    r = requests.post(
        f"{server_address}/api/v3/user/follow",
        json={"username": username},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    print(r.json())
    assert r.status_code == 201
