import pytest
import requests
from os import getenv
from datetime import datetime
from pony.orm import db_session, commit
import socialserver.db as db
from socialserver.util.auth import generate_key, generate_salt, hash_password

UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 " \
     "Mobile/15A372 Safari/604.1 "

"""
    test_db
    pytest fixture that creates an in-memory database with nothing in it
"""


@pytest.fixture
def test_db(monkeypatch):
    test_db = db.create_test_db()
    return test_db


"""
    server_address
    returns the url of the testing server,
    for tests that need to make requests to it
"""


@pytest.fixture
def server_address():
    addr = getenv("SOCIALSERVER_TEST_SERVER_ADDRESS", default=None)
    port = getenv("SOCIALSERVER_TEST_SERVER_PORT", default=None)

    return f"http://{'127.0.0.1' if addr is None else addr}:{'9801' if port is None else port}"


"""
    test_db_with_user
    
    creates a testdb with a user and a session
"""


@db_session
@pytest.fixture
def test_db_with_user():
    test_db = db.create_test_db()
    password = "password"
    password_salt = generate_salt()
    password_hash = hash_password(password, password_salt)
    test_db.User(
        username="test",
        display_name="test",
        password_hash=password_hash,
        password_salt=password_salt,
        creation_time=datetime.now(),
        account_attributes=[0],
        bio="",
        account_approved=True,
        is_legacy_account=False
    )
    # we're saving here, so we can create a session using this user
    commit()
    secret = generate_key()
    test_db.UserSession(
        access_token_hash=secret.hash,
        user=test_db.User.get(username="test"),
        creation_ip="127.0.0.1",
        creation_time=datetime.now(),
        last_access_time=datetime.now(),
        user_agent=UA
    )
    commit()
    return {
        "db": test_db,
        "username": "test",
        "password": "password",
        "access_token": secret.key
    }


"""
    create_user_with_request
    
    fires a request to server_address, to create a new user
"""


def create_user_with_request(serveraddress, username="username", password="password", display_name="name"):
    r = requests.post(f"{serveraddress}/api/v2/user",
                      json={
                          "display_name": display_name,
                          "username": username,
                          "password": password
                      })
    # we want to fail if this didn't work, since tests
    # will fail in strange ways if the account they
    # expect isn't made
    print(r.json())
    print(r.status_code)
    assert r.status_code == 201
    return r.json()


"""
    create_user_session_with_request
    
    takes username & password, and creates a user session
    returns the token.
"""


def create_user_session_with_request(serveraddress, username, password):
    r = requests.post(f"{serveraddress}/api/v2/user/session",
                      json={
                          "username": username,
                          "password": password
                      })

    # fail immediately if it didn't work
    assert r.status_code == 201


"""
    create_post_with_request
    
    creates a simple post using requests, to test feeds and the like.
    requires user auth token. doesn't support images
"""


def create_post_with_request(serveraddress, auth_token, text_content="Test Post"):
    r = requests.post(f"{serveraddress}/api/v2/post",
                      json={
                          "access_token": auth_token,
                          "text_content": text_content
                      })
    return r.json()['post_id']
