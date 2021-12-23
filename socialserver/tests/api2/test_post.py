# noinspection PyUnresolvedReferences
from socialserver.tests.util import test_db_with_user, server_address, create_user_session_with_request
import requests


def test_create_single_post(test_db_with_user, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db_with_user.get('db'))
    monkeypatch.setattr("socialserver.api.v2.post.db", test_db_with_user.get('db'))
    monkeypatch.setattr("socialserver.util.auth.db", test_db_with_user.get('db'))

    r = requests.post(f"{server_address}/api/v2/post/single",
                  json={
                      "access_token": test_db_with_user.get('access_token'),
                      "text_content": "Test Post"
                  })

    assert r.status_code == 200
    # blank database, so this should be post id 1.
    assert r.json()['post_id'] == 1
