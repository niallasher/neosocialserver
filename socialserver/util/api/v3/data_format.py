#  Copyright (c) Niall Asher 2022
from socialserver.constants import PostAdditionalContentTypes
from socialserver.db import db


def format_userdata_v3(
    user_object, current_user_object, include_header=False, include_bio=False, include_follower_info=False
):
    pfp_identifier = None
    pfp_blur_hash = None

    if user_object.profile_pic is not None:
        pfp_identifier = user_object.profile_pic.identifier
        pfp_blur_hash = user_object.profile_pic.blur_hash

    userdata = {
        "display_name": user_object.display_name,
        "username": user_object.username,
        "attributes": user_object.account_attributes,
        "profile_picture": {"identifier": pfp_identifier, "blur_hash": pfp_blur_hash},
        "followed": db.Follow.get(user=current_user_object, following=user_object) is not None
    }

    if include_header:
        header_identifier = None
        header_blur_hash = None

        if user_object.header_pic is not None:
            header_identifier = user_object.header_pic.identifier
            header_blur_hash = user_object.header_pic.blur_hash

        userdata["header_picture"] = {
            "identifier": header_identifier,
            "blur_hash": header_blur_hash,
        }

    if include_bio:
        userdata["bio"] = user_object.bio

    if include_follower_info:
        userdata["follower_count"] = user_object.followers.count()
        userdata["following_count"] = user_object.following.count()

    return userdata


def format_post_v3(post_object):
    # additional_content = post_object.additional_content

    additional_content_type = PostAdditionalContentTypes.NONE.value
    additional_content = []

    post_images = post_object.get_images
    video = post_object.video

    if len(post_images) >= 1:
        additional_content_type = PostAdditionalContentTypes.IMAGES.value
        for image in post_images:
            additional_content.append(
                {"identifier": image.identifier, "blurhash": image.blur_hash}
            )
    elif video is not None:
        additional_content_type = PostAdditionalContentTypes.VIDEO.value
        additional_content.append(
            {
                "identifier": video.identifier,
                "thumbnail_identifier": video.thumbnail.identifier,
                "thumbnail_blurhash": video.thumbnail.blur_hash,
            }
        )

    return {
        "id": post_object.id,
        "content": post_object.text,
        "creation_date": post_object.creation_time.timestamp(),
        "like_count": len(post_object.likes),
        "comment_count": len(post_object.comments),
        "additional_content_type": additional_content_type,
        "additional_content": additional_content,
    }
