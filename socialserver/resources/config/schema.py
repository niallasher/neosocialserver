#  Copyright (c) Niall Asher 2022

from pydantic import BaseModel, IPvAnyAddress, Field, validator
from socialserver.constants import MAX_PIXEL_RATIO
from typing import Literal


class _ServerConfigNetwork(BaseModel):
    host: IPvAnyAddress
    # 1-65535 is the valid TCP port range, hence the limit.
    port: int = Field(..., ge=1, le=65535)


class _ServerConfigMisc(BaseModel):
    enable_landing_page: bool


class _ServerConfigDatabase(BaseModel):
    connector: Literal["sqlite", "postgres"]
    filename: str
    username: str
    password: str
    database_name: str
    host: str


class _ServerConfigMediaImages(BaseModel):
    quality: int = Field(..., ge=1, le=100)
    post_quality: int = Field(..., ge=1, le=100)
    storage_dir: str
    # max size cannot be negative. god knows what would happen if it was.
    # probably not much. but you definitely wouldn't be uploading any images.
    max_image_request_size_mb: float = Field(..., ge=0)


class _ServerConfigMediaVideos(BaseModel):
    storage_dir: str


class _ServerConfigMedia(BaseModel):
    images: _ServerConfigMediaImages
    videos: _ServerConfigMediaVideos


class _ServerConfigAuthRegistration(BaseModel):
    enabled: bool
    approval_required: bool
    auto_approve_when_approval_disabled: bool


class _ServerConfigAuthTotp(BaseModel):
    replay_prevention_enabled: bool
    issuer: str
    # it makes no sense for a time in the future to be < 0,
    # and would just cause issues.
    unconfirmed_expiry_time: int = Field(..., ge=0)


class _ServerConfigAuth(BaseModel):
    registration: _ServerConfigAuthRegistration
    totp: _ServerConfigAuthTotp


class _ServerConfigPosts(BaseModel):
    silent_fail_on_double_report: bool


class _ServerConfigLegacyApiInterface(BaseModel):
    enable: bool
    image_pixel_ratio: int = Field(..., ge=0, le=MAX_PIXEL_RATIO)
    signup_enabled: bool
    deliver_full_post_images: bool
    report_legacy_version: bool
    enable_less_secure_password_change: bool


class ServerConfig(BaseModel):
    network: _ServerConfigNetwork
    misc: _ServerConfigMisc
    database: _ServerConfigDatabase
    media: _ServerConfigMedia
    auth: _ServerConfigAuth
    posts: _ServerConfigPosts
    legacy_api_interface: _ServerConfigLegacyApiInterface