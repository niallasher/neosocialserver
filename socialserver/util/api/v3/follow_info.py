#  Copyright (c) Niall Asher 2022

from socialserver.db import db
from socialserver.constants import FollowListSortTypes, ErrorCodes, FollowListListTypes
from socialserver.util.api.v3.data_format import format_userdata_v3
from socialserver.util.api.v3.error_format import format_error_return_v3
from pony.orm import select, desc


def get_follow_info_for_user(user_object: db.User, count: int, offset: int, sort_type: int,
                             list_type: int) -> (dict, int):

    def extract_correct_userdata(fe):
        if is_following_list:
            return format_userdata_v3(fe.following)
        else:
            return format_userdata_v3(fe.user)
        pass

    is_following_list = False
    if list_type == FollowListListTypes.FOLLOWERS:
        query = select(fe for fe in user_object.followers)
    elif list_type == FollowListListTypes.FOLLOWING:
        is_following_list = True
        query = select(fe for fe in user_object.following)

    # sort the query based on what the user's looking for.
    if sort_type == FollowListSortTypes.AGE_ASCENDING.value:
        query = query.order_by(lambda fe: fe.creation_time)
    elif sort_type == FollowListSortTypes.AGE_DESCENDING.value:
        query = query.order_by(lambda fe: desc(fe.creation_time))
    else:
        return format_error_return_v3(ErrorCodes.INVALID_SORT_TYPE, 400)

    fe_count = query.count()

    query = query.limit(count, offset=offset)

    # convert to a list
    query = query[::]

    user_objects = []
    for fe in query:
        user_objects.append(extract_correct_userdata(fe))

    return {
               "meta": {
                   "count": fe_count,
                   "reached_end": len(user_objects) < count
               },
               "follow_entries": user_objects
           }, 200
