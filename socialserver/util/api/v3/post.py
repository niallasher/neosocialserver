#  Copyright (c) Niall Asher 2022
from socialserver.constants import PostAdditionalContentTypes


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
