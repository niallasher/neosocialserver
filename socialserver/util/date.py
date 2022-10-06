#  Copyright (c) Niall Asher 2022

from datetime import datetime


def format_timestamp_string(datetime_object: datetime):
    return datetime_object.utcnow().isoformat()
