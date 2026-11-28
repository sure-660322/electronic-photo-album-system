"""请求与响应对象（接口约定 5.3）。字段校验给出中文说明并定位到字段。"""
import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from .errors import ApiError

Visibility = Literal["public", "private"]


def _require_text(value: str | None) -> str:
    if value is None or not value.strip():
        raise ValueError("不能为空")
    return value


class RegisterIn(BaseModel):
    username: str
    password: str
    password_confirmation: str
    email: EmailStr

    @field_validator("username", mode="before")
    @classmethod
    def strip_username(cls, value):
        if not isinstance(value, str):
            raise ValueError("用户名格式无效")
        value = value.strip()
        if not 1 <= len(value) <= 32:
            raise ValueError("用户名长度需在 1–32 个字符之间")
        return value

    @field_validator("email", mode="before")
    @classmethod
    def strip_email(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("password")
    @classmethod
    def check_password(cls, value):
        if not isinstance(value, str) or not 8 <= len(value) <= 128:
            raise ValueError("密码长度需在 8–128 个字符之间")
        return value

    @field_validator("password_confirmation")
    @classmethod
    def check_confirmation(cls, value, info):
        password = info.data.get("password")
        if password is not None and value != password:
            raise ValueError("两次密码不一致")
        return value


class LoginIn(BaseModel):
    username: str
    password: str

    @field_validator("username", mode="before")
    @classmethod
    def strip_username(cls, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("用户名不能为空")
        return value.strip()

    @field_validator("password")
    @classmethod
    def check_password(cls, value):
        if not isinstance(value, str) or not value:
            raise ValueError("密码不能为空")
        return value


class AlbumCreateIn(BaseModel):
    name: str
    category_id: int
    visibility: Visibility

    @field_validator("name", mode="before")
    @classmethod
    def check_name(cls, value):
        if not isinstance(value, str):
            raise ValueError("相册名称格式无效")
        value = value.strip()
        if not 1 <= len(value) <= 100:
            raise ValueError("相册名称长度需在 1–100 个字符之间")
        return value

    @field_validator("category_id")
    @classmethod
    def check_category(cls, value):
        if value is None:
            raise ValueError("请选择相册类别")
        return value


class AlbumUpdateIn(AlbumCreateIn):
    version: int

    @field_validator("version")
    @classmethod
    def check_version(cls, value):
        if not isinstance(value, int) or value < 1:
            raise ValueError("版本号需为正整数")
        return value


class UserSummary(BaseModel):
    id: int
    username: str


class AccountOut(BaseModel):
    id: int
    username: str
    email: str
    role: str


class CategoryOut(BaseModel):
    id: int
    name: str


class AlbumOut(BaseModel):
    id: int
    name: str
    visibility: str
    version: int
    owner_id: int
    category: CategoryOut
    created_at: datetime
    updated_at: datetime


class PhotoOut(BaseModel):
    id: int
    album_id: int
    uploader: UserSummary
    created_at: datetime
    thumbnail_url: str


class CommentOut(BaseModel):
    id: int
    photo_id: int
    author: UserSummary
    body: str
    created_at: datetime


class LikeStateOut(BaseModel):
    liked: bool
    like_count: int


class PhotoDetailOut(BaseModel):
    photo: PhotoOut
    original_url: str
    comments: list[CommentOut]
    like: LikeStateOut


def parse_upload_id(raw: str | None) -> uuid.UUID:
    """上传标识须为 UUID，否则按字段级校验错误返回。"""
    if not raw or not raw.strip():
        raise ApiError(422, "VALIDATION_ERROR", "缺少上传标识", field="upload_id")
    try:
        return uuid.UUID(raw.strip())
    except ValueError:
        raise ApiError(422, "VALIDATION_ERROR", "上传标识格式无效", field="upload_id")
