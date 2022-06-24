#  Copyright (c) Niall Asher 2022

from socialserver.util.test import test_db, server_address, create_user_with_request, follow_user_with_request
from socialserver.constants import FollowListListTypes, FollowListSortTypes
import requests


# FIXME: these tests aren't complete!
# pycharm keeps indenting headers like crazy. not sure why, but that's why it's how it is.

def test_get_following_list_empty(test_db, server_address):
    create_user_with_request(username="user2")
    r = requests.get(f"{server_address}/api/v3/user/follow_list", json={
        "sort_type": FollowListSortTypes.AGE_ASCENDING.value,
        "username": "user2",
        "count": "10",
        "offset": "0",
        "list_type": FollowListListTypes.FOLLOWING.value
    },
                     headers={
                         "Authorization": f"Bearer {test_db.access_token}"
                     })
    assert r.status_code == 200
    assert r.json()['meta']['count'] == 0
    assert len(r.json()['follow_entries']) == 0
