import pytest
from os import getenv
import socialserver.db as db

"""
    mem_db
    pytest fixture that creates an in-memory database with nothing in it
"""


@pytest.fixture
def mem_db(monkeypatch):
    mem_db = db.create_memory_db()
    return mem_db


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
