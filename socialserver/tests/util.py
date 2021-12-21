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
    mem_db
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
    create_test_user_api2

    creates a test user using api2
"""


def create_test_user_api2(addr, username="test", password="test", display_name="test"):
    requests.post(addr, json={
        "username": username,
        "display_name": display_name,
        "password": password
    })
    return SimpleNamespace(
        username = username,
        display_name = display_name,
        password = password
    )

"""
    get_session_token_api2
    
    logs in and returns the token using api2
"""