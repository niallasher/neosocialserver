#  Copyright (c) Niall Asher 2022

import requests
from socialserver.util.test import test_db, set_user_attributes_db, server_address, create_user_with_request
from socialserver.constants import AccountAttributes, ErrorCodes, ApprovalSortTypes
from socialserver.util.config import config


def test_get_user_approvals(test_db, server_address):
    # set user to be an admin
    set_user_attributes_db(test_db.db, test_db.username, [AccountAttributes.ADMIN.value])
    # make sure new accounts need to verify
    config.auth.registration.approval_required = True

    create_user_with_request(server_address, "user2", "password", "User2")

    r = requests.get(f"{server_address}/api/v3/admin/userApprovals",
                     json={
                         "count": 10,
                         "offset": 0,
                         "sort": ApprovalSortTypes.USERNAME_ALPHABETICAL.value
                     },
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200

    assert r.json()['meta']['reached_end'] == True
    assert r.json()['users'][0]['username'] == "user2"

    # set back to false
    config.auth.registration.approval_required = False


def test_get_user_approvals_empty(test_db, server_address):
    # set user to be an admin
    set_user_attributes_db(test_db.db, test_db.username, [AccountAttributes.ADMIN.value])

    r = requests.get(f"{server_address}/api/v3/admin/userApprovals",
                     json={
                         "count": 10,
                         "offset": 0,
                         "sort": ApprovalSortTypes.USERNAME_ALPHABETICAL.value
                     },
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200

    assert r.json()['meta']['reached_end'] == True
    assert len(r.json()['users']) == 0

    # set back to false
    config.auth.registration.approval_required = False


def test_get_user_approvals_filtered(test_db, server_address):
    # set user to be an admin
    set_user_attributes_db(test_db.db, test_db.username, [AccountAttributes.ADMIN.value])
    # make sure new accounts need to verify
    config.auth.registration.approval_required = True

    create_user_with_request(server_address, "user2", "password", "User2")
    create_user_with_request(server_address, "xuser3", "password", "User2")
    create_user_with_request(server_address, "xuser4", "password", "User2")
    create_user_with_request(server_address, "xuser5", "password", "User2")

    r = requests.get(f"{server_address}/api/v3/admin/userApprovals",
                     json={
                         "count": 10,
                         "offset": 0,
                         "sort": ApprovalSortTypes.USERNAME_ALPHABETICAL.value,
                         "filter": "xuser"
                     },
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200

    assert r.json()['meta']['reached_end'] == True
    assert r.json()['users'][0]['username'] == "xuser3"
    assert len(r.json()['users']) == 3

    # set back to false
    config.auth.registration.approval_required = False


def test_approve_user(test_db, server_address):
    # set user to be an admin
    set_user_attributes_db(test_db.db, test_db.username, [AccountAttributes.ADMIN.value])
    # make sure new accounts need to verify
    config.auth.registration.approval_required = True

    create_user_with_request(server_address, "user2", "password", "User2")

    r = requests.get(f"{server_address}/api/v3/admin/userApprovals",
                     json={
                         "count": 10,
                         "offset": 0,
                         "sort": ApprovalSortTypes.USERNAME_ALPHABETICAL.value
                     },
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200

    assert r.json()['meta']['reached_end'] == True
    assert r.json()['users'][0]['username'] == "user2"

    r = requests.patch(f"{server_address}/api/v3/admin/userApprovals",
                       json={
                           "username": "user2"
                       },
                       headers={
                           "Authorization": f"bearer {test_db.access_token}"
                       })
    assert r.status_code == 200

    # double check the user is gone from the list
    r = requests.get(f"{server_address}/api/v3/admin/userApprovals",
                     json={
                         "count": 10,
                         "offset": 0,
                         "sort": ApprovalSortTypes.USERNAME_ALPHABETICAL.value
                     },
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200

    assert r.json()['meta']['reached_end'] == True
    assert len(r.json()['users']) == 0

    # make sure the user still exists
    r = requests.get(f"{server_address}/api/v3/user/name_available",
                     json={
                         "username": "user2"
                     })
    assert r.status_code == 200
    assert r.json() is False

    # set back to false
    config.auth.registration.approval_required = False


def test_reject_user(test_db, server_address):
    # set user to be an admin
    set_user_attributes_db(test_db.db, test_db.username, [AccountAttributes.ADMIN.value])
    # make sure new accounts need to verify
    config.auth.registration.approval_required = True

    create_user_with_request(server_address, "user2", "password", "User2")

    r = requests.get(f"{server_address}/api/v3/admin/userApprovals",
                     json={
                         "count": 10,
                         "offset": 0,
                         "sort": ApprovalSortTypes.USERNAME_ALPHABETICAL.value
                     },
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200

    assert r.json()['meta']['reached_end'] == True
    assert r.json()['users'][0]['username'] == "user2"

    r = requests.delete(f"{server_address}/api/v3/admin/userApprovals",
                        json={
                            "username": "user2"
                        },
                        headers={
                            "Authorization": f"bearer {test_db.access_token}"
                        })
    assert r.status_code == 200

    # double check the user is gone from the list
    r = requests.get(f"{server_address}/api/v3/admin/userApprovals",
                     json={
                         "count": 10,
                         "offset": 0,
                         "sort": ApprovalSortTypes.USERNAME_ALPHABETICAL.value
                     },
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200

    assert r.json()['meta']['reached_end'] == True
    assert len(r.json()['users']) == 0

    # make sure the user still exists
    r = requests.get(f"{server_address}/api/v3/user/name_available",
                     json={
                         "username": "user22"
                     })
    assert r.status_code == 200
    assert r.json() is True

    # set back to false
    config.auth.registration.approval_required = False
