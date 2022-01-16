from socialserver.util.test import server_address, test_db
import requests


def test_invite_stub(server_address, test_db):
    r = requests.get(f"{server_address}/api/v1/invitecodes",
                     json={
                         "session_token": test_db.access_token
                     })
    assert r.status_code == 201
    # this should always be empty; we don't have invite codes in 3.x (at least not for now...)
    assert len(r.json()) == 0
