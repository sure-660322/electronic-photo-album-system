"""可重复执行的初始化：预置相册类别与演示账号。

用法（在 backend/ 目录、激活虚拟环境后）：
    python -m app.seed

已有类别与账号不会被改动，重复执行安全。
演示账号密码取自 .env 的 ALBUM_DEMO_PASSWORD / ALBUM_ADMIN_PASSWORD。
"""
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from .db import SessionLocal
from .models import Category, User
from .security import hash_password

PRESET_CATEGORIES = ["风景", "人物", "生活", "旅行"]

DEMO_ACCOUNTS = [
    # (用户名, 邮箱, 角色, 密码配置项)
    ("demo_a", "demo_a@example.com", "member", "demo"),
    ("demo_b", "demo_b@example.com", "member", "demo"),
    ("admin", "admin@example.com", "admin", "admin"),
]


def run_seed() -> None:
    from .config import get_settings

    settings = get_settings()
    passwords = {
        "demo": settings.album_demo_password,
        "admin": settings.album_admin_password,
    }

    with SessionLocal() as session:
        for name in PRESET_CATEGORIES:
            session.execute(
                pg_insert(Category)
                .values(name=name)
                .on_conflict_do_nothing(index_elements=["name"])
            )
        for username, email, role, password_key in DEMO_ACCOUNTS:
            session.execute(
                pg_insert(User)
                .values(
                    username=username,
                    email=email,
                    password_hash=hash_password(passwords[password_key]),
                    role=role,
                )
                .on_conflict_do_nothing(index_elements=["username"])
            )
        session.commit()

        categories = list(session.scalars(select(Category).order_by(Category.id)))
        users = list(session.scalars(select(User).order_by(User.id)))
        print(f"预置类别 {len(categories)} 个：{'、'.join(c.name for c in categories)}")
        print(
            "演示账号："
            + "、".join(
                f"{u.username}({u.role})" for u in users
                if u.username in {row[0] for row in DEMO_ACCOUNTS}
            )
        )


if __name__ == "__main__":
    run_seed()
