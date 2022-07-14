#  Copyright (c) Niall Asher 2022

from socialserver.util.output import console
from socialserver.constants import UNPROCESSED_POST_CHECK_INTERVAL
from socialserver.db import db
from pony.orm import select, db_session, commit
from threading import Thread
from time import sleep


@db_session
def _check_unprocessed_posts():
    posts = select(post for post in db.Post if post.processed is False)
    console.log(f"Checking post process statuses. {posts.count()} in queue.")
    for post in posts:
        ok_to_mark_processed = True
        post_images = list(filter(lambda x: x["type"] == "image", post.attachments))
        for media_entry in post_images:
            image = db.Image.get(identifier=media_entry["identifier"])
            if image.processed is False:
                ok_to_mark_processed = False
        if ok_to_mark_processed:
            post.processed = True
    commit()


def start_unprocessed_post_thread():
    def _run():
        while True:
            try:
                _check_unprocessed_posts()
                sleep(UNPROCESSED_POST_CHECK_INTERVAL)
            except KeyboardInterrupt:
                break

    console.log(
        f"Starting unprocessed post checking thread, interval={UNPROCESSED_POST_CHECK_INTERVAL}"
    )
    check_thread = Thread(target=_run, daemon=True)
    check_thread.start()
