#  Copyright (c) Niall Asher 2022

# noinspection PyUnresolvedReferences
from socialserver.util.test import (
    test_db,
    server_address,
    create_user_with_request,
    create_post_with_request,
    create_user_session_with_request,
)
import requests
from socialserver.constants import ReportReasons, AccountAttributes
from pony.orm import db_session, commit


def test_create_report(test_db, server_address):
    create_user_with_request(username="user2", password="password")

    at_two = create_user_session_with_request(username="user2", password="password")

    post_id = create_post_with_request(
        auth_token=at_two, text_content="valid opinion that I disagree with"
    )

    r = requests.post(
        f"{server_address}/api/v3/posts/report",
        json={
            "report_reason": [ReportReasons.DISCRIMINATION.value],
            "supplemental_info": "test data test data",
            "post_id": post_id,
        },
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    assert r.status_code == 201


def test_try_create_report_own_post(test_db, server_address):
    post_id = create_post_with_request(auth_token=test_db.access_token)

    r = requests.post(
        f"{server_address}/api/v3/posts/report",
        json={
            "report_reason": [ReportReasons.DISCRIMINATION.value],
            "supplemental_info": "test data test data",
            "post_id": post_id,
        },
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    assert r.status_code == 400


def test_create_report_missing_args(test_db, server_address):
    create_post_with_request(
        test_db.access_token, text_content="valid opinion that I disagree with"
    )

    r = requests.post(
        f"{server_address}/api/v3/posts/report",
        json={},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    assert r.status_code == 400


@db_session
def test_get_report_from_post_id(test_db, server_address):
    # make the user an admin, so we can read and modify reports
    test_db.db.User.get(username=test_db.username).account_attributes = [
        AccountAttributes.ADMIN.value
    ]
    commit()

    create_user_with_request(username="user2", password="password")
    at_two = create_user_session_with_request(username="user2", password="password")
    post_id = create_post_with_request(at_two, text_content="post")

    assert (
            requests.post(
                f"{server_address}/api/v3/posts/report",
                json={
                    "report_reason": [ReportReasons.ILLEGAL_CONTENT.value],
                    "supplemental_info": "i don't like this post very much, so it's bad",
                    "post_id": post_id,
                },
                headers={"Authorization": f"Bearer {test_db.access_token}"},
            ).status_code
            == 201
    )

    r = requests.get(
        f"{server_address}/api/v3/posts/report",
        json={"post_id": post_id},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    assert r.status_code == 201
    assert r.json()[0]["reporter"] == test_db.username
    assert (
            r.json()[0]["report_info"]["report_reasons"][0]
            == ReportReasons.ILLEGAL_CONTENT.value
    )
