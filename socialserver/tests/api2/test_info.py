from socialserver.tests.fixtures import server_address
from socialserver.constants import SERVER_VERSION
from socialserver import constants
import requests
from unittest.mock import patch


def test_info(server_address, monkeypatch):
    req = requests.get(f"{server_address}/api/v2/server/info")
    assert req.status_code == 201
