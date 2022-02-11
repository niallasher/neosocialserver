#  Copyright (c) Niall Asher 2022

# noinspection PyUnresolvedReferences
from socialserver.util.test import server_address
import requests


def test_get_server_info(server_address):
    r = requests.get(f"{server_address}/api/v1/info")
    assert r.status_code == 201
