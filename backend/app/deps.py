"""路由依赖：数据库会话、当前身份、角色与写请求来源检查。"""
from typing import Iterator

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from .config import get_settings
from .db import SessionLocal
from .errors import ApiError
from .models import User
from .security import SESSION_COOKIE, resolve_token_subject


def get_db() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_current_user(
    request: Request, session: Session = Depends(get_db)
) -> User:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise ApiError(401, "AUTH_REQUIRED", "请先登录")
    subject = resolve_token_subject(token)
    if subject is None or not subject.isdigit():
        raise ApiError(401, "AUTH_REQUIRED", "会话无效或已过期，请重新登录")
    user = session.get(User, int(subject))
    if user is None:
        raise ApiError(401, "AUTH_REQUIRED", "账户不存在，请重新登录")
    return user


def require_member(user: User = Depends(get_current_user)) -> User:
    """创建相册、修改相册、上传图片限普通用户。"""
    if user.role != "member":
        raise ApiError(403, "ROLE_FORBIDDEN", "当前账户无权执行该操作")
    return user


def check_write_origin(request: Request) -> None:
    """写请求核对 Origin：浏览器会带 Origin，来源不在白名单时拒绝；
    无 Origin 的非浏览器客户端（如测试脚本）不在此拦截。"""
    origin = request.headers.get("origin")
    if origin is None:
        return
    if origin not in get_settings().allowed_origins:
        raise ApiError(403, "ORIGIN_FORBIDDEN", "请求来源校验失败")
