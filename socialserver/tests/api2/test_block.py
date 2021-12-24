# pycharm isn't detecting fixture usage, so we're
# disabling PyUnresolvedReferences for the import.
# noinspection PyUnresolvedReferences
from socialserver.tests.util import test_db_with_user, server_address, create_user_with_request
from socialserver.constants import ErrorCodes
import requests


def test_block_user(test_db_with_user, server_address, monkeypatch):
    # create a second user to block
    create_user_with_request(server_address, username="user2", password="hunter22")

    block_req = requests.post(f"{server_address}/api/v2/block/user",
                              json={
                                  "access_token": test_db_with_user.get("access_token"),
                                  "username": "user2"
                              })

    assert block_req.status_code == 201


def test_block_user_invalid_token(test_db_with_user, server_address, monkeypatch):
    # create a second user to block
    create_user_with_request(server_address, username="user2", password="hunter22")

    block_req = requests.post(f"{server_address}/api/v2/block/user",
                              json={
                                  "access_token": "lolnope",
                                  "username": "user2"
                              })

    assert block_req.status_code == 401
    assert block_req.json()['error'] == ErrorCodes.TOKEN_INVALID.value


def test_try_block_already_tried_user(test_db_with_user, server_address, monkeypatch):
    # create a second user to block
    create_user_with_request(server_address, username="user2", password="hunter22")

    requests.post(f"{server_address}/api/v2/block/user",
                  json={
                      "access_token": test_db_with_user.get("access_token"),
                      "username": "user2"
                  })

    block_req = requests.post(f"{server_address}/api/v2/block/user",
                              json={
                                  "access_token": test_db_with_user.get("access_token"),
                                  "username": "user2"
                              })

    assert block_req.status_code == 400
    assert block_req.json()['error'] == ErrorCodes.BLOCK_ALREADY_EXISTS.value


def test_block_user_missing_info(test_db_with_user, server_address, monkeypatch):
    # create a second user to block
    create_user_with_request(server_address, username="user2", password="hunter22")

    block_req = requests.post(f"{server_address}/api/v2/block/user",
                              json={})

    assert block_req.status_code == 400


def test_remove_block(test_db_with_user, server_address, monkeypatch):
    # create a second user to block
    create_user_with_request(server_address, username="user2", password="hunter22")

    # we'll need to create a block if we want to remove it :)
    requests.post(f"{server_address}/api/v2/block/user",
                  json={
                      "access_token": test_db_with_user.get("access_token"),
                      "username": "user2"
                  })
    block_del_req = requests.delete(f"{server_address}/api/v2/block/user",
                                    json={
                                        "access_token": test_db_with_user.get("access_token"),
                                        "username": "user2"
                                    })

    assert block_del_req.status_code == 204


def test_remove_block_not_exists(test_db_with_user, server_address, monkeypatch):
    # create a second user to block
    create_user_with_request(server_address, username="user2", password="hunter22")

    block_del_req = requests.delete(f"{server_address}/api/v2/block/user",
                                    json={
                                        "access_token": test_db_with_user.get("access_token"),
                                        "username": "user2"
                                    })

    assert block_del_req.status_code == 404
    assert block_del_req.json()['error'] == ErrorCodes.CANNOT_FIND_BLOCK_ENTRY.value


def test_remove_block_missing_info(test_db_with_user, server_address, monkeypatch):
    # create a second user to block
    create_user_with_request(server_address, username="user2", password="hunter22")

    block_del_req = requests.delete(f"{server_address}/api/v2/block/user",
                                    json={})

    assert block_del_req.status_code == 400


def test_remove_block_invalid_token(test_db_with_user, server_address, monkeypatch):
    # create a second user to block
    create_user_with_request(server_address, username="user2", password="hunter22")

    block_del_req = requests.delete(f"{server_address}/api/v2/block/user",
                                    json={
                                        "access_token": "not_correct",
                                        "username": "user2"
                                    })

    assert block_del_req.status_code == 401
    assert block_del_req.json()['error'] == ErrorCodes.TOKEN_INVALID.value
