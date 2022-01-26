# noinspection PyUnresolvedReferences
from socialserver.util.test import server_address, test_db, create_post_with_request, create_user_with_request, \
    create_user_session_with_request, set_user_attributes_db
from socialserver.constants import LegacyErrorCodes, AccountAttributes
import requests


def test_delete_post_admin_legacy(test_db, server_address):
    # make test user all powerful
    set_user_attributes_db(test_db.db,
                           test_db.username,
                           [AccountAttributes.ADMIN.value])

    create_user_with_request(server_address, username="test2", password="password")
    session_token = create_user_session_with_request(server_address, username="test2", password="password")
    post_id = create_post_with_request(server_address, session_token)

    r = requests.delete(f"{server_address}/api/v1/admin/postdel",
                        json={
                            "session_token": test_db.access_token,
                            "post_id": post_id
                        })
    assert r.status_code == 201

    # attempt to get the post
    r = requests.get(f"{server_address}/api/v1/posts",
                     json={
                         "session_token": test_db.access_token,
                         "post_id": post_id
                     })
    # compatibility strikes again :(
    # this is how it must be.
    assert r.status_code == 401
    assert r.json()['err'] == LegacyErrorCodes.POST_NOT_FOUND.value


def test_delete_post_user_not_admin_admin_legacy(test_db, server_address):
    create_user_with_request(server_address, username="test2", password="password")
    session_token = create_user_session_with_request(server_address, username="test2", password="password")
    post_id = create_post_with_request(server_address, session_token)

    r = requests.delete(f"{server_address}/api/v1/admin/postdel",
                        json={
                            "session_token": test_db.access_token,
                            "post_id": post_id
                        })
    assert r.status_code == 401
    assert r.json()['err'] == LegacyErrorCodes.USER_NOT_ADMIN.value

    # attempt to get the post
    r = requests.get(f"{server_address}/api/v1/posts",
                     json={
                         "session_token": test_db.access_token,
                         "post_id": post_id
                     })
    # compatibility strikes again :(
    # this is how it must be.
    assert r.status_code == 201


def test_delete_post_invalid_post_admin_legacy(test_db, server_address):
    # make test user all powerful
    set_user_attributes_db(test_db.db,
                           test_db.username,
                           [AccountAttributes.ADMIN.value])

    r = requests.delete(f"{server_address}/api/v1/admin/postdel",
                        json={
                            "session_token": test_db.access_token,
                            "post_id": 373
                        })
    assert r.status_code == 404
    assert r.json()['err'] == LegacyErrorCodes.POST_NOT_FOUND.value
