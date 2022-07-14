#  Copyright (c) Niall Asher 2022
from socialserver.db import db
from socialserver.util.output import console
from socialserver.util.config import config
from pony.orm import select, db_session


# run under the following conditions:
#   - auth.registration.approval_required is false
#   - accounts are in the approval queue
#   - auth.registration.auto_approve_when_approval_disabled is true


@db_session
def _approve_all_queued_user_creation_requests():
    console.log(
        "[bold]Auto approving users stuck in queue; approval_required changed to false!"
    )
    unapproved_users = select(
        user for user in db.User if user.account_approved is False
    )
    for user in unapproved_users:
        user.account_approved = True
    console.log(f"[bold]Approved {len(unapproved_users)} users!")


# remove any unprocessed images (and posts that contained them).
@db_session
def _remove_stuck_resources():
    console.log("[bold]Removing stuck images (and posts)...")
    unprocessed_images = select(image for image in db.Image if image.processed is False)
    for image in unprocessed_images:
        for post in image.associated_posts:
            # TODO: this might need improvement, for UX purposes. If the server dies and restarts,
            # the user will have no clue their post can't go through...
            console.log(
                f"Removing post, id={post.id}, due to a dependency on an unprocessed image."
            )
            post.delete()
        console.log(
            f"Removing image, id={image.id}, due to it being unprocessed when server shut down last."
        )
        image.delete()


# run on startup
def maintenance():
    console.log("Running startup maintenance")
    if (
        config.auth.registration.approval_required
        and config.auth.registration.auto_approve_when_approval_disabled
    ):
        _approve_all_queued_user_creation_requests()
    _remove_stuck_resources()
