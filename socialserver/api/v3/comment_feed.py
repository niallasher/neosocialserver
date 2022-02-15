#  Copyright (c) Niall Asher 2022

from flask_restful import Resource, reqparse
from socialserver.constants import MAX_FEED_GET_COUNT, ErrorCodes, CommentFeedSortTypes
from socialserver.db import db
from socialserver.util.auth import auth_reqd, get_user_from_auth_header
from pony.orm import db_session, select, desc, count


class CommentFeed(Resource):

    @db_session
    @auth_reqd
    def get(self):
        parser = reqparse.RequestParser()

        parser.add_argument('post_id', type=int, required=True)
        parser.add_argument('count', type=int, required=True)
        parser.add_argument('offset', type=int, required=True)
        # one of CommentFeedSortTypes
        parser.add_argument('sort', type=int, required=True)

        args = parser.parse_args()

        requesting_user_db = get_user_from_auth_header()

        post = db.Post.get(id=args['post_id'])
        if post is None:
            return {"error": ErrorCodes.POST_NOT_FOUND.value}, 404

        # we don't want to show comments from blocked users
        blocks = select(b.blocking for b in db.Block
                        if b.user == requesting_user_db)

        comments = select(comment for comment in db.Comment
                          if comment.user not in blocks
                          and comment.post is post)

        if args['sort'] == CommentFeedSortTypes.CREATION_TIME_DESCENDING.value:
            comments.order_by(desc(db.Comment.creation_time))
        elif args['sort'] == CommentFeedSortTypes.LIKE_COUNT.value:
            comments.order_by(desc(count(db.Comment.likes)))
        else:
            return {"error": ErrorCodes.INVALID_SORT_TYPE.value}, 400

        comments.limit(args['count'], offset=args['offset'])

        comments_formatted = []
        for comment in comments:
            comments_formatted.append({
                "comment": {
                    "id": comment.id,
                    "content": comment.text,
                    "creation_time": comment.creation_time.timestamp(),
                    "like_count": len(comment.likes)
                },
                "user": {
                    "display_name": comment.user.display_name,
                    "username": comment.user.username,
                    "attributes": comment.user.account_attributes,
                    "own_comment": comment.user == requesting_user_db
                }
            })

        return {
            "meta": {
                "reached_end": len(comments_formatted) < args['count']
            },
            "comments": comments_formatted
        }
