#  Copyright (c) Niall Asher 2022

# pycharm isn't detecting fixture usage, so we're
# disabling PyUnresolvedReferences for the import.
# noinspection PyUnresolvedReferences
from socialserver.util.test import test_db, server_address, create_user_with_request
from socialserver.constants import ErrorCodes
import requests


def test_block_user(test_db, server_address, monkeypatch):
    # create a second user to block
    create_user_with_request(server_address, username="user2", password="hunter22")

    block_req = requests.post(f"{server_address}/api/v3/user/block",
                              json={
                                  "username": "user2"
                              },
                              headers={
                                  "Authorization": f"Bearer {test_db.access_token}"
                              })

    assert block_req.status_code == 201


def test_block_user_invalid_token(test_db, server_address, monkeypatch):
    # create a second user to block
    create_user_with_request(server_address, username="user2", password="hunter22")

    block_req = requests.post(f"{server_address}/api/v3/user/block",
                              json={
                                  "username": "user2"
                              },
                              headers={
                                  "Authorization": f"Bearer invalid"
                              })

    assert block_req.status_code == 401
    assert block_req.json()['error'] == ErrorCodes.TOKEN_INVALID.value


def test_try_block_already_tried_user(test_db, server_address, monkeypatch):
    # create a second user to block
    create_user_with_request(server_address, username="user2", password="hunter22")

    requests.post(f"{server_address}/api/v3/user/block",
                  json={
                      "username": "user2"
                  },
                  headers={
                      "Authorization": f"Bearer {test_db.access_token}"
                  })

    block_req = requests.post(f"{server_address}/api/v3/user/block",
                              json={
                                  "username": "user2"
                              },
                              headers={
                                  "Authorization": f"Bearer {test_db.access_token}"
                              })

    assert block_req.status_code == 400
    assert block_req.json()['error'] == ErrorCodes.BLOCK_ALREADY_EXISTS.value


def test_block_user_missing_info(test_db, server_address, monkeypatch):
    # create a second user to block
    create_user_with_request(server_address, username="user2", password="hunter22")

    block_req = requests.post(f"{server_address}/api/v3/user/block",
                              json={},
                              headers={
                                  "Authorization": f"Bearer {test_db.access_token}"
                              })

    assert block_req.status_code == 400


def test_remove_block(test_db, server_address, monkeypatch):
    # create a second user to block
    create_user_with_request(server_address, username="user2", password="hunter22")

    # we'll need to create a block if we want to remove it :)
    requests.post(f"{server_address}/api/v3/user/block",
                  json={
                      "username": "user2"
                  },
                  headers={
                      "Authorization": f"Bearer {test_db.access_token}"
                  })

    block_del_req = requests.delete(f"{server_address}/api/v3/user/block",
                                    json={
                                        "username": "user2"
                                    },
                                    headers={
                                        "Authorization": f"Bearer {test_db.access_token}"
                                    })

    assert block_del_req.status_code == 204


def test_remove_block_not_exists(test_db, server_address, monkeypatch):
    # create a second user to block
    create_user_with_request(server_address, username="user2", password="hunter22")

    block_del_req = requests.delete(f"{server_address}/api/v3/user/block",
                                    json={
                                        "username": "user2"
                                    },
                                    headers={
                                        "Authorization": f"Bearer {test_db.access_token}"
                                    })

    assert block_del_req.status_code == 404
    assert block_del_req.json()['error'] == ErrorCodes.CANNOT_FIND_BLOCK_ENTRY.value


def test_remove_block_missing_info(test_db, server_address, monkeypatch):
    # create a second user to block
    create_user_with_request(server_address, username="user2", password="hunter22")

    block_del_req = requests.delete(f"{server_address}/api/v3/user/block",
                                    json={},
                                    headers={
                                        "Authorization": f"Bearer {test_db.access_token}"
                                    })

    assert block_del_req.status_code == 400


def test_remove_block_invalid_token(test_db, server_address, monkeypatch):
    # create a second user to block
    create_user_with_request(server_address, username="user2", password="hunter22")

    block_del_req = requests.delete(f"{server_address}/api/v3/user/block",
                                    json={
                                        "username": "user2"
                                    },
                                    headers={
                                        "Authorization": f"Bearer invalid"
                                    })

    assert block_del_req.status_code == 401
    assert block_del_req.json()['error'] == ErrorCodes.TOKEN_INVALID.value
