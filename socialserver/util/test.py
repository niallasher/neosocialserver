import pony.orm
import pytest
import requests
from os import getenv
from socialserver.db import create_test_db
import magic
from attrdict import AttrDict
from json import dumps
from base64 import urlsafe_b64encode
from socialserver.static.test_data.test_image import TEST_IMAGE_B64

UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 " \
     "Mobile/15A372 Safari/604.1 "

"""
    test_db
    pytest fixture that creates an in-memory database with a pre-made user account
    and session.
"""


@pytest.fixture
def test_db(monkeypatch):
    test_db = create_test_db()
    monkeypatch_api_db(pytest.MonkeyPatch(), test_db)
    create_user_with_request(get_server_address(),
                             username="test",
                             password="password",
                             display_name="test")
    access_token = create_user_session_with_request(get_server_address(),
                                                    username="test",
                                                    password="password")
    return AttrDict({
        "db": test_db,
        "username": "test",
        "password": "password",
        "display_name": "test",
        "access_token": access_token
    })


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
    monkeypatch.setattr("socialserver.util.image.IMAGE_DIR", "/tmp/socialserver_image_testing")
    monkeypatch.setattr("socialserver.api.v3.image.IMAGE_DIR", "/tmp/socialserver_image_testing")
    monkeypatch.setattr("socialserver.util.auth.db", db)
    monkeypatch.setattr("socialserver.util.image.db", db)
    monkeypatch.setattr("socialserver.api.v3.block.db", db)
    monkeypatch.setattr("socialserver.api.v3.feed.db", db)
    monkeypatch.setattr("socialserver.api.v3.follow.db", db)
    monkeypatch.setattr("socialserver.api.v3.image.db", db)
    monkeypatch.setattr("socialserver.api.v3.post.db", db)
    monkeypatch.setattr("socialserver.api.v3.report.db", db)
    monkeypatch.setattr("socialserver.api.v3.user.db", db)
    monkeypatch.setattr("socialserver.api.v3.user_session.db", db)
    monkeypatch.setattr("socialserver.api.v3.username_available.db", db)
    # legacy api
    monkeypatch.setattr("socialserver.api.legacy.user.db", db)
    monkeypatch.setattr("socialserver.api.legacy.comment_filter.filter_by_post.db", db)
    monkeypatch.setattr("socialserver.api.legacy.usermod.db", db)
    monkeypatch.setattr("socialserver.api.legacy.authentication.db", db)
    monkeypatch.setattr("socialserver.api.legacy.post_filter.filter_by_user.db", db)
    monkeypatch.setattr("socialserver.api.legacy.post.db", db)
    monkeypatch.setattr("socialserver.api.legacy.user_deauth.db", db)
    monkeypatch.setattr("socialserver.api.legacy.modqueue.db", db)
    monkeypatch.setattr("socialserver.api.legacy.like.db", db)
    monkeypatch.setattr("socialserver.api.legacy.invite_codes.db", db)
    monkeypatch.setattr("socialserver.api.legacy.follows.db", db)
    monkeypatch.setattr("socialserver.api.legacy.follower.db", db)
    monkeypatch.setattr("socialserver.api.legacy.comment.db", db)
    monkeypatch.setattr("socialserver.api.legacy.block.db", db)
    monkeypatch.setattr("socialserver.api.legacy.bio.db", db)
    return None


"""
"""

"""
    create_user_with_request
    
    fires a request to server_address, to create a new user
"""


def create_user_with_request(serveraddress, username="username", password="password", display_name="name"):
    r = requests.post(f"{serveraddress}/api/v3/user",
                      json={
                          "display_name": display_name,
                          "username": username,
                          "password": password
                      })
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


def create_user_session_with_request(serveraddress, username, password):
    r = requests.post(f"{serveraddress}/api/v3/user/session",
                      json={
                          "username": username,
                          "password": password
                      })

    # fail immediately if it didn't work
    assert r.status_code == 200
    return r.json()['access_token']


"""
    create_post_with_request
    
    creates a simple post using requests, to test feeds and the like.
    requires user auth token. doesn't support images
"""


def create_post_with_request(serveraddress, auth_token, text_content="Test Post"):
    r = requests.post(f"{serveraddress}/api/v3/post/single",
                      json={
                          "text_content": text_content
                      },
                      headers={
                          "Authorization": f"Bearer {auth_token}"
                      })
    assert r.status_code == 200
    return r.json()['post_id']


"""
    follow_user_with_request
    
    follows a user account using the local api
"""


def follow_user_with_request(serveraddress: str, auth_token: str, username: str):
    r = requests.post(f"{serveraddress}/api/v3/follow/user",
                      json={
                          "username": username
                      },
                      headers={
                          "Authorization": f"Bearer {auth_token}"
                      })
    assert r.status_code == 201
