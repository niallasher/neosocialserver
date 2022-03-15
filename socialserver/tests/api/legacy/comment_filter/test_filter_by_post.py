#  Copyright (c) Niall Asher 2022

# noinspection PyUnresolvedReferences
from socialserver.util.test import test_db, create_post_with_request, server_address
import requests


def test_get_comments_on_post_no_comments_legacy(test_db, server_address):
    post_id = create_post_with_request(test_db.access_token)
    r = requests.get(
        f"{server_address}/api/v1/comments/byPost",
        json={
            "session_token": test_db.access_token,
            "post_id": post_id,
            "count": 10,
            "offset": 0,
        },
    )

    print(r.json())
    assert r.status_code == 201
