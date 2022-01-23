from socialserver.util.test import test_db, server_address, create_user_session_with_request
from socialserver.constants import ErrorCodes
from socialserver.util.config import config
import pyotp
import requests


def test_add_totp_to_account(test_db, server_address):
    r = requests.post(f"{server_address}/api/v3/user/2fa",
                      json={
                          "password": test_db.password
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 201
    secret = r.json()['secret']
    totp_object = pyotp.TOTP(secret)
    totp_now = totp_object.now()
    r = requests.post(f"{server_address}/api/v3/user/2fa/verify",
                      json={
                          "totp": totp_now
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 201
    r = requests.get(f"{server_address}/api/v3/user/2fa",
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200
    assert r.json() is True


def test_add_totp_to_account_invalid_password_totp(test_db, server_address):
    r = requests.post(f"{server_address}/api/v3/user/2fa",
                      json={
                          "password": "not_correct"
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 401
    assert r.json()['error'] == ErrorCodes.INCORRECT_PASSWORD.value
    r = requests.get(f"{server_address}/api/v3/user/2fa",
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200
    assert r.json() is False


def test_add_totp_to_account_invalid_verification_totp(test_db, server_address):
    r = requests.post(f"{server_address}/api/v3/user/2fa",
                      json={
                          "password": test_db.password
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 201
    secret = r.json()['secret']
    r = requests.post(f"{server_address}/api/v3/user/2fa/verify",
                      json={
                          # if this is actually the totp when the test is run,
                          # i won't know what to believe anymore.
                          "totp": "123456"
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 400
    assert r.json()['error'] == ErrorCodes.TOTP_INCORRECT.value
    r = requests.get(f"{server_address}/api/v3/user/2fa",
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200
    assert r.json() is False


def test_verify_totp_no_totp_added(test_db, server_address):
    r = requests.post(f"{server_address}/api/v3/user/2fa/verify",
                      json={
                          "totp": 123456
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 400
    assert r.json()['error'] == ErrorCodes.TOTP_NOT_ACTIVE.value


def test_verify_totp_totp_already_added(test_db, server_address):
    r = requests.post(f"{server_address}/api/v3/user/2fa",
                      json={
                          "password": test_db.password
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 201
    secret = r.json()['secret']
    totp_object = pyotp.TOTP(secret)
    totp_now = totp_object.now()
    r = requests.post(f"{server_address}/api/v3/user/2fa/verify",
                      json={
                          "totp": totp_now
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 201
    r = requests.get(f"{server_address}/api/v3/user/2fa",
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200
    assert r.json() is True
    r = requests.post(f"{server_address}/api/v3/user/2fa/verify",
                      json={
                          "totp": totp_now
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 400
    assert r.json()['error'] == ErrorCodes.TOTP_ALREADY_ACTIVE.value


def test_add_totp_to_account_no_verification_totp(test_db, server_address):
    r = requests.post(f"{server_address}/api/v3/user/2fa",
                      json={
                          "password": test_db.password
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 201
    r = requests.get(f"{server_address}/api/v3/user/2fa",
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200
    assert r.json() is False


def test_remove_totp_from_account(test_db, server_address):
    r = requests.post(f"{server_address}/api/v3/user/2fa",
                      json={
                          "password": test_db.password
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 201
    secret = r.json()['secret']
    totp_object = pyotp.TOTP(secret)
    totp_now = totp_object.now()
    r = requests.post(f"{server_address}/api/v3/user/2fa/verify",
                      json={
                          "totp": totp_now
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 201
    r = requests.get(f"{server_address}/api/v3/user/2fa",
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200
    assert r.json() is True
    r = requests.delete(f"{server_address}/api/v3/user/2fa",
                        json={
                            "password": test_db.password
                        },
                        headers={
                            "Authorization": f"bearer {test_db.access_token}"
                        })
    assert r.status_code == 200
    r = requests.get(f"{server_address}/api/v3/user/2fa",
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200
    assert r.json() is False


def test_remove_totp_from_account_invalid_password(test_db, server_address):
    r = requests.post(f"{server_address}/api/v3/user/2fa",
                      json={
                          "password": test_db.password
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 201
    secret = r.json()['secret']
    totp_object = pyotp.TOTP(secret)
    totp_now = totp_object.now()
    r = requests.post(f"{server_address}/api/v3/user/2fa/verify",
                      json={
                          "totp": totp_now
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 201
    r = requests.get(f"{server_address}/api/v3/user/2fa",
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200
    assert r.json() is True
    r = requests.delete(f"{server_address}/api/v3/user/2fa",
                        json={
                            "password": "incorrect_password_goes_here"
                        },
                        headers={
                            "Authorization": f"bearer {test_db.access_token}"
                        })
    assert r.status_code == 401
    r = requests.get(f"{server_address}/api/v3/user/2fa",
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200
    assert r.json() is True


def test_login_totp_enabled(test_db, server_address):
    # disable totp replay prevention, since we're doing this rapid fire
    # and i'm not waiting 30 seconds for a single test :)
    # (will add separate tests for replay prevention!)
    config.auth.totp.replay_prevention_enabled = False
    r = requests.post(f"{server_address}/api/v3/user/2fa",
                      json={
                          "password": test_db.password
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 201
    secret = r.json()['secret']
    totp_object = pyotp.TOTP(secret)
    totp_now = totp_object.now()
    r = requests.post(f"{server_address}/api/v3/user/2fa/verify",
                      json={
                          "totp": totp_now
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 201
    r = requests.get(f"{server_address}/api/v3/user/2fa",
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200
    assert r.json() is True
    r = requests.post(f"{server_address}/api/v3/user/session",
                      json={
                          "username": test_db.username,
                          "password": test_db.password,
                          "totp": totp_object.now()
                      })
    assert r.status_code == 200


def test_login_totp_enabled_invalid_code(test_db, server_address):
    # disable totp replay prevention, since we're doing this rapid fire
    # and i'm not waiting 30 seconds for a single test :)
    # (will add separate tests for replay prevention!)
    config.auth.totp.replay_prevention_enabled = False
    r = requests.post(f"{server_address}/api/v3/user/2fa",
                      json={
                          "password": test_db.password
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 201
    secret = r.json()['secret']
    totp_object = pyotp.TOTP(secret)
    totp_now = totp_object.now()
    r = requests.post(f"{server_address}/api/v3/user/2fa/verify",
                      json={
                          "totp": totp_now
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 201
    r = requests.get(f"{server_address}/api/v3/user/2fa",
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200
    assert r.json() is True
    r = requests.post(f"{server_address}/api/v3/user/session",
                      json={
                          "username": test_db.username,
                          "password": test_db.password,
                          # plz don't be the actual code plz plz plz
                          "totp": 123456
                      })
    assert r.status_code == 401
    assert r.json()['error'] == ErrorCodes.TOTP_INCORRECT.value


def test_login_totp_enabled_no_totp_code(test_db, server_address):
    # disable totp replay prevention, since we're doing this rapid fire
    # and i'm not waiting 30 seconds for a single test :)
    # (will add separate tests for replay prevention!)
    config.auth.totp.replay_prevention_enabled = False
    r = requests.post(f"{server_address}/api/v3/user/2fa",
                      json={
                          "password": test_db.password
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 201
    secret = r.json()['secret']
    totp_object = pyotp.TOTP(secret)
    totp_now = totp_object.now()
    r = requests.post(f"{server_address}/api/v3/user/2fa/verify",
                      json={
                          "totp": totp_now
                      },
                      headers={
                          "Authorization": f"bearer {test_db.access_token}"
                      })
    assert r.status_code == 201
    r = requests.get(f"{server_address}/api/v3/user/2fa",
                     headers={
                         "Authorization": f"bearer {test_db.access_token}"
                     })
    assert r.status_code == 200
    assert r.json() is True
    r = requests.post(f"{server_address}/api/v3/user/session",
                      json={
                          "username": test_db.username,
                          "password": test_db.password,
                      })
    assert r.status_code == 400
    assert r.json()['error'] == ErrorCodes.TOTP_REQUIRED.value
