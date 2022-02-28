#  Copyright (c) Niall Asher 2022

# noinspection PyUnresolvedReferences
from socialserver.util.test import test_db, create_post_with_request, server_address, image_data_binary
from socialserver.constants import DISPLAY_NAME_MAX_LEN
from secrets import token_urlsafe
import requests


def test_update_display_name_legacy(test_db, server_address, monkeypatch):
    r = requests.post(f"{server_address}/api/v1/usermod",
                      json={
                          "session_token": test_db.access_token,
                          "display_name": "new name"
                      })
    assert r.status_code == 201
    r2 = requests.get(f"{server_address}/api/v1/users",
                      json={
                          "session_token": test_db.access_token,
                          "username": test_db.username
                      })
    assert r2.json()['displayName'] == "new name"


def test_update_display_name_too_long_legacy(test_db, server_address, monkeypatch):
    r = requests.post(f"{server_address}/api/v1/usermod",
                      json={
                          "session_token": test_db.access_token,
                          "display_name": token_urlsafe(DISPLAY_NAME_MAX_LEN + 1)
                      })
    assert r.status_code == 400
    r2 = requests.get(f"{server_address}/api/v1/users",
                      json={
                          "session_token": test_db.access_token,
                          "username": test_db.username
                      })
    assert r2.json()['displayName'] == "test"


def test_update_username_legacy(test_db, server_address, monkeypatch):
    r = requests.post(f"{server_address}/api/v1/usermod",
                      json={
                          "session_token": test_db.access_token,
                          "username": "new_username"
                      })
    assert r.status_code == 201
    r2 = requests.get(f"{server_address}/api/v1/users",
                      json={
                          "session_token": test_db.access_token,
                      })
    assert r2.status_code == 200
    assert r2.json()['displayName'] == "test"


def test_update_username_invalid_legacy(test_db, server_address):
    r = requests.post(f"{server_address}/api/v1/usermod",
                      json={
                          "session_token": test_db.access_token,
                          "username": "#invalid!"
                      })
    assert r.status_code == 400


def test_update_avatar_legacy(test_db, server_address, image_data_binary):
    image_identifier = requests.post(f"{server_address}/api/v3/image",
                                     files={
                                         "original_image": image_data_binary
                                     },
                                     headers={
                                         "Authorization": f"Bearer {test_db.access_token}"
                                     }).json()['identifier']
    r = requests.post(f"{server_address}/api/v1/usermod",
                      json={
                          "session_token": test_db.access_token,
                          "avatar_hash": image_identifier
                      })
    assert r.status_code == 201
    r2 = requests.get(f"{server_address}/api/v1/users",
                      json={
                          "session_token": test_db.access_token,
                          "username": test_db.username
                      })
    print(r2.json())
