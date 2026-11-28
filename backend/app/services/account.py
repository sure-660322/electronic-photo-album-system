"""账户服务：注册、凭据验证与令牌解析（登录设计 01/02）。"""
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..errors import ApiError
from ..models import User
from ..schemas import RegisterIn
from ..security import hash_password, issue_token, verify_password


class AccountService:
    def register(self, session: Session, data: RegisterIn) -> User:
        existing = session.scalar(
            select(User).where(User.username == data.username)
        )
        if existing is not None:
            raise ApiError(409, "USERNAME_TAKEN", "该用户名已被占用", field="username")
        user = User(
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
            role="member",
        )
        session.add(user)
        try:
            session.commit()
        except IntegrityError:
            # 并发注册同名账户时由唯一约束兜底。
            session.rollback()
            raise ApiError(409, "USERNAME_TAKEN", "该用户名已被占用", field="username")
        return user

    def authenticate(self, session: Session, username: str, password: str) -> User:
        user = session.scalar(select(User).where(User.username == username))
        if user is None or not verify_password(password, user.password_hash):
            raise ApiError(401, "INVALID_CREDENTIALS", "用户名或密码错误")
        return user

    def resolve_user(self, session: Session, subject: str) -> User | None:
        if not subject.isdigit():
            return None
        return session.get(User, int(subject))

    issue_token = staticmethod(issue_token)
