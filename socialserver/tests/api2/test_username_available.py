# noinspection PyUnresolvedReferences
from socialserver.tests.util import test_db_with_user, server_address, test_db
import requests


def test_username_available_name_taken(test_db_with_user, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.username_available.db", test_db_with_user.get('db'))
    r = requests.get(f"{server_address}/api/v2/user/name_available",
                     json={
                         "username": test_db_with_user.get('username')
                     })

    assert r.status_code == 200
    assert r.json() == False


def test_username_available_name_not_taken(test_db, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.username_available.db", test_db)
    r = requests.get(f"{server_address}/api/v2/user/name_available",
                     json={
                         "username": "username"
                     })

    assert r.status_code == 200
    assert r.json() == True


def test_username_available_missing_data(test_db, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.username_available.db", test_db)
    r = requests.get(f"{server_address}/api/v2/user/name_available", json={})

    assert r.status_code == 400
