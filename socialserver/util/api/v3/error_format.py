#  Copyright (c) Niall Asher 2022
from socialserver.constants import ErrorCodes


def format_error_return_v3(error: ErrorCodes, return_code: int):
    return {"error": error.value}, return_code
