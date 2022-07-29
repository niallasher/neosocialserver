#  Copyright (c) Niall Asher 2022
from socialserver.constants import AccountAttributes, SERVER_VERSION
from socialserver.db import db
from pony import orm
from datetime import datetime
from rich import print


def get_data():
    users = orm.select(u for u in db.User)
    admins = orm.select(u for u in db.User if AccountAttributes.ADMIN.value in u.account_attributes)
    mods = orm.select(u for u in db.User if AccountAttributes.MODERATOR.value in u.account_attributes)
    verified_users = orm.select(u for u in db.User if AccountAttributes.VERIFIED.value in u.account_attributes)
    unapproved_users = orm.select(u for u in db.User if u.account_approved is False)
    enabled_totp_objects = orm.select(t for t in db.Totp if t.confirmed is True)
    blocks = orm.select(b for b in db.Block)
    sessions = orm.select(s for s in db.UserSession)
    posts = orm.select(p for p in db.Post)
    posts_under_moderation = orm.select(p for p in db.Post if p.under_moderation is True)
    post_reports_open = orm.select(r for r in db.PostReport if r.active is True)
    post_reports_closed = orm.select(r for r in db.PostReport if r.active is False)
    post_hashtags = orm.select(h for h in db.Hashtag)
    comments = orm.select(c for c in db.Comment)
    images = orm.select(i for i in db.Image)
    videos = orm.select(v for v in db.Video)

    results = {
        "Users": [
            {
                "field_name": "User count",
                "value": users.count()
            },
            {
                "field_name": "User(s) with admin attribute",
                "value": admins.count()
            },
            {
                "field_name": "User(s) with moderator attribute",
                "value": mods.count()
            },
            {
                "field_name": "User(s) with verified attribute",
                "value": verified_users.count()
            },
            {
                "field_name": "User(s) with active TOTP 2FA",
                "value": enabled_totp_objects.count()
            },
            {
                "field_name": "Unapproved user(s)",
                "value": unapproved_users.count()
            },
            {
                "field_name": "Block records",
                "value": blocks.count()
            },
            {
                "field_name": "User session count",
                "value": sessions.count()
            }
        ],
        "Posts": [
            {
                "field_name": "Post count (incl. under moderation)",
                "value": posts.count()
            },
            {
                "field_name": "Post(s) under moderation",
                "value": posts_under_moderation.count()
            },
            {
                "field_name": "Post report count (active)",
                "value": post_reports_open.count()
            },
            {
                "field_name": "Post report count (inactive)",
                "value": post_reports_closed.count()
            },
            {
                "field_name": "Unique hashtag count",
                "value": post_hashtags.count()
            }
        ],
        "Comments": [
            {
                "field_name": "Comment count",
                "value": comments.count()
            }
        ],
        "Media": [
            {
                "field_name": "Image count",
                "value": images.count()
            },
            {
                "field_name": "Video count",
                "value": videos.count()
            }
        ]
    }
    return results


def print_server_statistics():
    results = get_data()
    print("\n\n")
    print("Statistics Report")
    print(f"Server version {SERVER_VERSION}")
    print(f"Generated {datetime.now().isoformat()}")
    for r in results.keys():
        print(f"[bold]=> {r}")
        for rd in results[r]:
            print(f"{rd['field_name']}: {rd['value']}")
    print("\n\n")
