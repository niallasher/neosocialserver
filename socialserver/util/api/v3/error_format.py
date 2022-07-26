#  Copyright (c) Niall Asher 2022
from socialserver.constants import ErrorCodes


def format_error_return_v3(error: ErrorCodes, return_code: int, supplemental_data: dict or None = None):
    return_dict = {"error": error.value}
    if supplemental_data is not None:
        for key in supplemental_data.keys():
            return_dict[key] = supplemental_data[key]
    return return_dict, return_code
