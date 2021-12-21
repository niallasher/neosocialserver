import pytest
from os import getenv
from datetime import datetime
from pony.orm import db_session, commit
import socialserver.db as db
from socialserver.util.auth import generate_key, generate_salt, hash_password
from types import SimpleNamespace
import requests

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
    salt = generate_salt()
    password = "password"
    password_hash = hash_password(password, salt)
    test_db.User(
        username="test",
        display_name="test",
        password_hash=password_hash,
        password_salt=salt,
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
