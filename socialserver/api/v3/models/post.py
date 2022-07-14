#  Copyright (c) Niall Asher 2022
from pydantic import BaseModel, validator, Extra
from socialserver.db import db

class InvalidAttachmentEntryException(Exception):
    pass

class AttachmentEntryModel(BaseModel):
    type: str
    identifier: str

    @validator("type")
    def type_validation(cls, value, values):
        # TODO: make this a constant value in socialserver.constants!
        if value not in ["image","video"]:
            raise InvalidAttachmentEntryException
        # fun fact! if you leave this out, the field will always be none!
        # other fun fact! i learnt this through pain.
        return value

    class Config():
        # this is very important; we need to make sure
        # there are no extra keys present before we store
        # the attachment information!
        extra = Extra.forbid
