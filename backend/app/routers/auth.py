"""认证路由：注册、登录、会话恢复与退出（登录设计 02）。"""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..deps import get_current_user, get_db
from ..errors import ApiError
from ..models import User
from ..schemas import AccountOut, LoginIn, RegisterIn
from ..security import SESSION_COOKIE
from ..services.account import AccountService
from ..config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])
service = AccountService()


def _account_view(user: User) -> AccountOut:
    return AccountOut(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
    )


def _session_response(user: User, status_code: int = 200) -> JSONResponse:
    settings = get_settings()
    content = _account_view(user).model_dump(mode="json")
    response = JSONResponse(status_code=status_code, content=content)
    response.set_cookie(
        key=SESSION_COOKIE,
        value=service.issue_token(user.id),
        max_age=settings.album_session_minutes * 60,
        httponly=True,
        samesite="lax",
        path="/api",
    )
    return response


@router.post("/register", status_code=201)
def register(data: RegisterIn, session: Session = Depends(get_db)):
    user = service.register(session, data)
    return _account_view(user)


@router.post("/login")
def login(data: LoginIn, session: Session = Depends(get_db)):
    user = service.authenticate(session, data.username, data.password)
    return _session_response(user)


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return _account_view(user)


@router.post("/logout")
def logout():
    """清除会话 Cookie，供演示时在两个账号间切换。"""
    response = JSONResponse(content={"ok": True})
    response.delete_cookie(key=SESSION_COOKIE, path="/api")
    return response
