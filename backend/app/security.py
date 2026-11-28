"""密码哈希与 JWT 会话令牌。Cookie 由路由层设置，这里只负责令牌本身。"""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from .config import get_settings

settings = get_settings()

SESSION_COOKIE = "album_session"
TOKEN_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("ascii"))
    except ValueError:
        return False


def issue_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.album_session_minutes),
    }
    return jwt.encode(payload, settings.album_jwt_secret, algorithm=TOKEN_ALGORITHM)


def resolve_token_subject(token: str) -> str | None:
    """令牌无效或过期时返回 None，由调用方按 AUTH_REQUIRED 处理。"""
    try:
        payload = jwt.decode(
            token, settings.album_jwt_secret, algorithms=[TOKEN_ALGORITHM]
        )
    except jwt.InvalidTokenError:
        return None
    subject = payload.get("sub")
    return subject if isinstance(subject, str) else None
