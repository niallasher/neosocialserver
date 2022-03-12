#  Copyright (c) Niall Asher 2022

# noinspection PyUnresolvedReferences
from socialserver.util.test import (
    server_address,
    test_db,
    create_post_with_request,
    create_user_with_request,
    create_user_session_with_request,
    set_user_attributes_db,
)
from socialserver.constants import LegacyErrorCodes, AccountAttributes
import requests


def test_get_modqueue_legacy(test_db, server_address):
    # make user a moderator
    set_user_attributes_db(
        test_db.db, test_db.username, [AccountAttributes.MODERATOR.value]
    )

    r = requests.get(
        f"{server_address}/api/v1/modqueue",
        json={"session_token": test_db.access_token, "count": 10, "offset": 0},
    )

    assert r.status_code == 201
    assert len(r.json()) == 0


def test_get_not_mod_or_admin_modqueue_legacy(test_db, server_address):
    r = requests.get(
        f"{server_address}/api/v1/modqueue",
        json={"session_token": test_db.access_token, "count": 10, "offset": 0},
    )

    assert r.status_code == 401
    assert (
            r.json()["err"]
            == LegacyErrorCodes.INSUFFICIENT_PERMISSIONS_TO_ACCESS_MODQUEUE.value
    )


def test_add_post_modqueue_legacy(test_db, server_address):
    # make user a moderator
    set_user_attributes_db(
        test_db.db, test_db.username, [AccountAttributes.MODERATOR.value]
    )

    create_user_with_request(username="test2", password="password")
    user_session = create_user_session_with_request(
        username="test2", password="password"
    )

    post_id = create_post_with_request(user_session, text_content="bad opinion.")

    # add the post to the modqueue
    r = requests.post(
        f"{server_address}/api/v1/modqueue",
        json={"session_token": test_db.access_token, "post_id": post_id},
    )

    assert r.status_code == 201

    # check it's in the queue
    r = requests.get(
        f"{server_address}/api/v1/modqueue",
        json={"session_token": test_db.access_token, "count": 10, "offset": 0},
    )

    assert r.status_code == 201
    assert len(r.json()) == 1
    assert r.json()[0] == post_id


def test_add_post_not_mod_or_admin_modqueue_legacy(test_db, server_address):
    create_user_with_request(username="test2", password="password")
    user_session = create_user_session_with_request(
        username="test2", password="password"
    )

    post_id = create_post_with_request(user_session, text_content="bad opinion.")

    # add the post to the modqueue
    r = requests.post(
        f"{server_address}/api/v1/modqueue",
        json={"session_token": test_db.access_token, "post_id": post_id},
    )

    assert r.status_code == 401
    assert (
            r.json()["err"]
            == LegacyErrorCodes.INSUFFICIENT_PERMISSIONS_TO_ACCESS_MODQUEUE.value
    )


def test_queued_post_not_visible_modqueue_legacy(test_db, server_address):
    # make user a moderator
    set_user_attributes_db(
        test_db.db, test_db.username, [AccountAttributes.MODERATOR.value]
    )

    create_user_with_request(username="test2", password="password")
    user_session = create_user_session_with_request(
        username="test2", password="password"
    )

    post_id = create_post_with_request(user_session, text_content="bad opinion.")

    # add the post to the modqueue
    r = requests.post(
        f"{server_address}/api/v1/modqueue",
        json={"session_token": test_db.access_token, "post_id": post_id},
    )

    assert r.status_code == 201

    # check it's not showing up in the main post feed
    r = requests.get(
        f"{server_address}/api/v1/posts",
        json={"session_token": test_db.access_token, "count": 10, "offset": 0},
    )

    assert r.status_code == 201
    assert len(r.json()) == 0
    assert post_id not in r.json()


def test_remove_post_from_modqueue_legacy(test_db, server_address):
    # make user a moderator
    set_user_attributes_db(
        test_db.db, test_db.username, [AccountAttributes.MODERATOR.value]
    )

    create_user_with_request(username="test2", password="password")
    user_session = create_user_session_with_request(
        username="test2", password="password"
    )

    post_id = create_post_with_request(user_session, text_content="bad opinion.")

    # add the post to the modqueue
    r = requests.post(
        f"{server_address}/api/v1/modqueue",
        json={"session_token": test_db.access_token, "post_id": post_id},
    )

    assert r.status_code == 201

    # remove it from the queue
    r = requests.delete(
        f"{server_address}/api/v1/modqueue",
        json={"session_token": test_db.access_token, "post_id": post_id},
    )

    assert r.status_code == 201

    # check it's gone from the queue
    r = requests.get(
        f"{server_address}/api/v1/modqueue",
        json={"session_token": test_db.access_token, "count": 10, "offset": 0},
    )

    assert r.status_code == 201
    assert len(r.json()) == 0


def test_remove_post_not_mod_or_admin_from_modqueue_legacy(test_db, server_address):
    # make user a moderator
    set_user_attributes_db(
        test_db.db, test_db.username, [AccountAttributes.MODERATOR.value]
    )

    create_user_with_request(username="test2", password="password")
    user_session = create_user_session_with_request(
        username="test2", password="password"
    )

    post_id = create_post_with_request(user_session, text_content="bad opinion.")

    # add the post to the modqueue
    r = requests.post(
        f"{server_address}/api/v1/modqueue",
        json={"session_token": test_db.access_token, "post_id": post_id},
    )

    assert r.status_code == 201

    # strip moderator account of all it's rights
    set_user_attributes_db(test_db.db, test_db.username, [])

    # attempt to remove it from the queue (not using the moderator account)
    r = requests.delete(
        f"{server_address}/api/v1/modqueue",
        json={"session_token": test_db.access_token, "post_id": post_id},
    )

    assert r.status_code == 401
    assert (
            r.json()["err"]
            == LegacyErrorCodes.INSUFFICIENT_PERMISSIONS_TO_ACCESS_MODQUEUE.value
    )

    # check it's not showing up in the main post feed
    r = requests.get(
        f"{server_address}/api/v1/posts",
        json={"session_token": test_db.access_token, "count": 10, "offset": 0},
    )

    assert r.status_code == 201
    assert len(r.json()) == 0
    assert post_id not in r.json()


def test_try_get_moderated_post_legacy(test_db, server_address):
    # make user a moderator
    set_user_attributes_db(
        test_db.db, test_db.username, [AccountAttributes.MODERATOR.value]
    )

    create_user_with_request(username="test2", password="password")
    user_session = create_user_session_with_request(
        username="test2", password="password"
    )

    post_id = create_post_with_request(user_session, text_content="bad opinion.")

    # add the post to the modqueue
    r = requests.post(
        f"{server_address}/api/v1/modqueue",
        json={"session_token": test_db.access_token, "post_id": post_id},
    )

    assert r.status_code == 201

    # try to get the moderated post id
    r = requests.get(
        f"{server_address}/api/v1/posts",
        json={"session_token": test_db.access_token, "post_id": post_id},
    )

    assert r.status_code == 201
    assert r.json()["username"] == "test2"


def test_try_get_moderated_post_not_mod_or_admin_legacy(test_db, server_address):
    # make user a moderator
    set_user_attributes_db(
        test_db.db, test_db.username, [AccountAttributes.MODERATOR.value]
    )

    create_user_with_request(username="test2", password="password")
    user_session = create_user_session_with_request(
        username="test2", password="password"
    )

    post_id = create_post_with_request(user_session, text_content="bad opinion.")

    # add the post to the modqueue
    r = requests.post(
        f"{server_address}/api/v1/modqueue",
        json={"session_token": test_db.access_token, "post_id": post_id},
    )

    assert r.status_code == 201

    # no more moderation for you.
    set_user_attributes_db(test_db.db, test_db.username, [])

    # try to get the moderated post id
    r = requests.get(
        f"{server_address}/api/v1/posts",
        json={"session_token": test_db.access_token, "post_id": post_id},
    )
    assert r.status_code == 401
    assert (
            r.json()["err"] == LegacyErrorCodes.INSUFFICIENT_PERMISSIONS_TO_VIEW_POST.value
    )
