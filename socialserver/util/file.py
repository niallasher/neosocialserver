#  Copyright (c) Niall Asher 2022

from math import ceil
from functools import wraps
from flask import make_response, jsonify, abort, request
from socialserver.constants import ErrorCodes

"""
    mb_to_b
    convert megabytes to bytes, rounding up
"""


def mb_to_b(mb_count: float) -> int:
    return ceil(mb_count * 1e+6)


"""
    b_to_mb
    convert bytes to megabytes 
"""


def b_to_mb(b_count: int) -> float:
    return b_count / 1e+6


"""
    max_req_size
    decorator to discard requests above a certain size
"""


def max_req_size(max_len_bytes: int):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            content_length = request.content_length
            if content_length is not None and content_length > max_len_bytes:
                abort(
                    make_response(
                        jsonify(
                            error=ErrorCodes.REQUEST_TOO_LARGE.value
                        ), 413
                    )
                )
            return f(*args, **kwargs)

        return wrapper

    return decorator
