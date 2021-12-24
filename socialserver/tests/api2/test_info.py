# pycharm isn't detecting fixture usage, so we're
# disabling PyUnresolvedReferences for the import.
# noinspection PyUnresolvedReferences
from socialserver.util.test import server_address
import requests


def test_info(server_address, monkeypatch):
    req = requests.get(f"{server_address}/api/v2/server/info")
    assert req.status_code == 201
