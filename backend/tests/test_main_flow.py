"""主流程集成测试：对应 issue #37 验收标准。

前置条件：本地 Docker 数据库已启动（仓库根目录 `docker compose up -d --wait db`），
且根目录 .env 已配置 ALBUM_DB_PASSWORD / ALBUM_JWT_SECRET。
在 backend/ 目录运行：python -m pytest
"""
import io
import random
import string
import struct
import uuid
import zlib

import pytest
from httpx import ASGITransport, AsyncClient
from PIL import Image

from app.db import SessionLocal
from app.main import app
from app.models import Album, Photo, User
from app.seed import run_seed
from app.services.storage import LocalPhotoStorage


def _png_bytes(width: int = 64, height: int = 48, color=(120, 160, 90)) -> bytes:
    image = Image.new("RGB", (width, height), color)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _png_padded_to(target: int) -> bytes:
    """在 IEND 前插入辅助块，把 PNG 凑到恰好 target 字节且仍然可解码。"""
    base = _png_bytes(600, 600)
    payload_len = target - len(base) - 12
    chunk = struct.pack(">I", payload_len) + b"paDd" + b"x" * payload_len
    chunk += struct.pack(">I", zlib.crc32(chunk[4:]) & 0xFFFFFFFF)
    return base[:-12] + chunk + base[-12:]


def _gif_bytes() -> bytes:
    image = Image.new("RGB", (80, 40), (30, 90, 160))
    buffer = io.BytesIO()
    image.save(buffer, format="GIF")
    return buffer.getvalue()


def _random_username(prefix: str) -> str:
    tail = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{prefix}_{tail}"


@pytest.fixture(scope="session", autouse=True)
def _seed():
    run_seed()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def _new_session_client() -> AsyncClient:
    """独立会话的客户端：登录响应的 Set-Cookie 存入自身 cookie jar。"""
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.fixture
async def users(client: AsyncClient):
    """注册并登录两个临时账号；测试结束后清理其数据与上传文件。"""
    created = []

    async def make(prefix: str) -> AsyncClient:
        username = _random_username(prefix)
        password = "pass-word-123"
        response = await client.post(
            "/api/auth/register",
            json={
                "username": username,
                "password": password,
                "password_confirmation": password,
                "email": f"{username}@example.com",
            },
        )
        assert response.status_code == 201, response.text
        ac = _new_session_client()
        login = await ac.post(
            "/api/auth/login", json={"username": username, "password": password}
        )
        assert login.status_code == 200
        created.append((username, ac))
        return ac

    yield make

    for _, ac in created:
        await ac.aclose()
    _cleanup_users([username for username, _ in created])


def _cleanup_users(usernames: list[str]) -> None:
    from sqlalchemy import select

    storage = LocalPhotoStorage()
    with SessionLocal() as session:
        users = list(
            session.scalars(select(User).where(User.username.in_(usernames)))
        )
        for user in users:
            photos = list(
                session.scalars(
                    select(Photo).where(Photo.uploader_id == user.id)
                )
            )
            for photo in photos:
                relative_dir = "/".join(photo.original_path.split("/")[:3])
                storage.remove_dir(relative_dir)
                session.delete(photo)
            for album in list(
                session.scalars(select(Album).where(Album.owner_id == user.id))
            ):
                session.delete(album)
            session.delete(user)
        session.commit()


async def _get_category_id(client: AsyncClient, name: str) -> int:
    response = await client.get("/api/categories")
    assert response.status_code == 200
    for item in response.json()["items"]:
        if item["name"] == name:
            return item["id"]
    raise AssertionError(f"预置类别 {name} 不存在")


# ---- 注册 / 登录 / 会话恢复 ----


async def test_register_password_mismatch(client: AsyncClient):
    response = await client.post(
        "/api/auth/register",
        json={
            "username": _random_username("u"),
            "password": "pass-word-123",
            "password_confirmation": "pass-word-456",
            "email": "x@example.com",
        },
    )
    assert response.status_code == 422
    body = response.json()["error"]
    assert body["code"] == "VALIDATION_ERROR"
    assert body["field"] == "password_confirmation"


async def test_register_duplicate_username(client: AsyncClient, users):
    ac = await users("dup")
    me = await ac.get("/api/auth/me")
    username = me.json()["username"]
    response = await client.post(
        "/api/auth/register",
        json={
            "username": username,
            "password": "pass-word-123",
            "password_confirmation": "pass-word-123",
            "email": "dup@example.com",
        },
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "USERNAME_TAKEN"


async def test_password_stored_hashed(client: AsyncClient, users):
    ac = await users("hash")
    me = await ac.get("/api/auth/me")
    username = me.json()["username"]
    with SessionLocal() as session:
        from sqlalchemy import select

        user = session.scalar(select(User).where(User.username == username))
        assert user.password_hash != "pass-word-123"
        assert user.password_hash.startswith("$2")


async def test_login_invalid_credentials(client: AsyncClient, users):
    await users("bad")
    response = await client.post(
        "/api/auth/login",
        json={"username": "nobody-x", "password": "pass-word-123"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


async def test_session_restore_and_logout(client: AsyncClient, users):
    ac = await users("sess")
    me = await ac.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["role"] == "member"
    await ac.post("/api/auth/logout")
    me2 = await ac.get("/api/auth/me")
    assert me2.status_code == 401
    assert me2.json()["error"]["code"] == "AUTH_REQUIRED"


async def test_admin_account_from_seed(client: AsyncClient):
    login = await client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "album-admin-123"},
    )
    assert login.status_code == 200, login.text
    assert login.json()["role"] == "admin"


# ---- 相册 ----


async def test_create_album_and_scope(client: AsyncClient, users):
    a, b = await users("albuma"), await users("albumb")
    category_id = await _get_category_id(a, "风景")
    created = await a.post(
        "/api/albums",
        json={"name": "公开相册", "category_id": category_id, "visibility": "public"},
    )
    assert created.status_code == 201, created.text
    album = created.json()
    assert album["version"] == 1
    assert album["owner_id"] == (await a.get("/api/auth/me")).json()["id"]

    mine = await a.get("/api/albums", params={"scope": "mine"})
    assert [item["id"] for item in mine.json()["items"]] == [album["id"]]

    visible = await b.get("/api/albums")
    assert album["id"] in [item["id"] for item in visible.json()["items"]]


async def test_update_album_validation(client: AsyncClient, users):
    a = await users("upd")
    other = await users("updo")
    category_id = await _get_category_id(a, "生活")
    album = (
        await a.post(
            "/api/albums",
            json={"name": "原名称", "category_id": category_id, "visibility": "public"},
        )
    ).json()

    # 非所有者修改：404
    resp = await other.put(
        f"/api/albums/{album['id']}",
        json={
            "name": "越权改名",
            "category_id": category_id,
            "visibility": "public",
            "version": 1,
        },
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "ALBUM_UNAVAILABLE"

    # 正常修改：版本 +1
    resp = await a.put(
        f"/api/albums/{album['id']}",
        json={
            "name": "新名称",
            "category_id": category_id,
            "visibility": "private",
            "version": 1,
        },
    )
    assert resp.status_code == 200
    assert resp.json()["version"] == 2
    assert resp.json()["visibility"] == "private"

    # 旧版本再改：409
    resp = await a.put(
        f"/api/albums/{album['id']}",
        json={
            "name": "再改",
            "category_id": category_id,
            "visibility": "private",
            "version": 1,
        },
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "ALBUM_VERSION_CONFLICT"

    # 名称过长：422 定位 name
    resp = await a.put(
        f"/api/albums/{album['id']}",
        json={
            "name": "长" * 101,
            "category_id": category_id,
            "visibility": "private",
            "version": 2,
        },
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["field"] == "name"


async def test_private_album_visibility(client: AsyncClient, users):
    a, b = await users("priva"), await users("privb")
    category_id = await _get_category_id(a, "旅行")
    album = (
        await a.post(
            "/api/albums",
            json={"name": "私有相册", "category_id": category_id, "visibility": "private"},
        )
    ).json()

    visible = await b.get("/api/albums")
    assert album["id"] not in [item["id"] for item in visible.json()["items"]]
    resp = await b.get(f"/api/albums/{album['id']}")
    assert resp.status_code == 404
    resp = await b.get(f"/api/albums/{album['id']}/photos")
    assert resp.status_code == 404
    # 本人可见
    resp = await a.get(f"/api/albums/{album['id']}")
    assert resp.status_code == 200


async def test_admin_cannot_create_album(client: AsyncClient):
    ac = _new_session_client()
    login = await ac.post(
        "/api/auth/login",
        json={"username": "admin", "password": "album-admin-123"},
    )
    assert login.status_code == 200
    category_id = (
        (await ac.get("/api/categories")).json()["items"][0]["id"]
    )
    resp = await ac.post(
        "/api/albums",
        json={"name": "管理员相册", "category_id": category_id, "visibility": "public"},
    )
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "ROLE_FORBIDDEN"
    await ac.aclose()


async def test_admin_cannot_view_private_album(client: AsyncClient, users):
    a = await users("admp")
    ac = _new_session_client()
    await ac.post(
        "/api/auth/login",
        json={"username": "admin", "password": "album-admin-123"},
    )
    category_id = await _get_category_id(a, "风景")
    album = (
        await a.post(
            "/api/albums",
            json={"name": "管理员不可见", "category_id": category_id, "visibility": "private"},
        )
    ).json()
    resp = await ac.get(f"/api/albums/{album['id']}")
    assert resp.status_code == 404
    await ac.aclose()


# ---- 上传与浏览 ----


async def test_upload_and_browse_flow(client: AsyncClient, users):
    a, b = await users("upa"), await users("upb")
    category_id = await _get_category_id(a, "风景")
    album = (
        await a.post(
            "/api/albums",
            json={"name": "上传演示", "category_id": category_id, "visibility": "public"},
        )
    ).json()

    upload_id = str(uuid.uuid4())
    png = _png_bytes(400, 300)
    resp = await a.post(
        f"/api/albums/{album['id']}/photos",
        files={"file": ("photo.png", png, "image/png")},
        data={"upload_id": upload_id},
    )
    assert resp.status_code == 201, resp.text
    photo = resp.json()
    assert photo["album_id"] == album["id"]
    assert photo["thumbnail_url"] == f"/api/photos/{photo['id']}/thumbnail"

    # 同一 upload_id 重试：200 且同一照片
    resp2 = await a.post(
        f"/api/albums/{album['id']}/photos",
        files={"file": ("photo.png", png, "image/png")},
        data={"upload_id": upload_id},
    )
    assert resp2.status_code == 200
    assert resp2.json()["id"] == photo["id"]

    # 元数据入库、缩略图生成
    with SessionLocal() as session:
        from sqlalchemy import select

        row = session.get(Photo, photo["id"])
        assert row is not None
        assert row.size_bytes == len(png)
        assert row.media_type == "image/png"
        assert row.original_path.endswith("original.png")
        assert row.thumbnail_path.endswith("thumbnail.png")
        thumb = Image.open(
            (LocalPhotoStorage().resolve(row.thumbnail_path))
        )
        assert max(thumb.size) <= 320

    # B 浏览公开照片
    photos = await b.get(f"/api/albums/{album['id']}/photos")
    assert [p["id"] for p in photos.json()["items"]] == [photo["id"]]
    detail = await b.get(f"/api/photos/{photo['id']}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["original_url"] == f"/api/photos/{photo['id']}/original"
    assert body["comments"] == []
    assert body["like"] == {"liked": False, "like_count": 0}

    original = await b.get(body["original_url"])
    assert original.status_code == 200
    assert original.headers["cache-control"] == "no-store"
    assert original.content == png
    thumb_resp = await b.get(photo["thumbnail_url"])
    assert thumb_resp.status_code == 200
    assert thumb_resp.headers["content-type"].startswith("image/png")

    # GIF 上传（首帧缩略图）
    resp = await a.post(
        f"/api/albums/{album['id']}/photos",
        files={"file": ("anim.gif", _gif_bytes(), "image/gif")},
        data={"upload_id": str(uuid.uuid4())},
    )
    assert resp.status_code == 201

    # 越权上传到他人相册
    resp = await b.post(
        f"/api/albums/{album['id']}/photos",
        files={"file": ("x.png", png, "image/png")},
        data={"upload_id": str(uuid.uuid4())},
    )
    assert resp.status_code == 404

    # 改私有后 B 全链路被拒、A 正常
    await a.put(
        f"/api/albums/{album['id']}",
        json={
            "name": "上传演示",
            "category_id": category_id,
            "visibility": "private",
            "version": album["version"],
        },
    )
    for path in (
        f"/api/albums/{album['id']}/photos",
        f"/api/photos/{photo['id']}",
        f"/api/photos/{photo['id']}/original",
        f"/api/photos/{photo['id']}/thumbnail",
        f"/api/albums/{album['id']}",
    ):
        resp = await b.get(path)
        assert resp.status_code == 404, path
    resp = await a.get(f"/api/photos/{photo['id']}")
    assert resp.status_code == 200


async def test_upload_rejections(client: AsyncClient, users):
    a = await users("rej")
    category_id = await _get_category_id(a, "人物")
    album = (
        await a.post(
            "/api/albums",
            json={"name": "校验演示", "category_id": category_id, "visibility": "public"},
        )
    ).json()

    # 超过 10MB（10,000,001 字节）
    resp = await a.post(
        f"/api/albums/{album['id']}/photos",
        files={"file": ("big.png", b"\x89PNG" + b"0" * 10_000_000, "image/png")},
        data={"upload_id": str(uuid.uuid4())},
    )
    assert resp.status_code == 413
    assert resp.json()["error"]["code"] == "IMAGE_TOO_LARGE"

    # 非 jpg/png/gif 内容（BMP）
    bmp = io.BytesIO()
    Image.new("RGB", (10, 10)).save(bmp, format="BMP")
    resp = await a.post(
        f"/api/albums/{album['id']}/photos",
        files={"file": ("x.bmp", bmp.getvalue(), "image/bmp")},
        data={"upload_id": str(uuid.uuid4())},
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "INVALID_IMAGE"

    # 损坏的 PNG
    resp = await a.post(
        f"/api/albums/{album['id']}/photos",
        files={"file": ("x.png", b"\x89PNG\r\n\x1a\nbroken", "image/png")},
        data={"upload_id": str(uuid.uuid4())},
    )
    assert resp.status_code == 422

    # upload_id 格式无效
    resp = await a.post(
        f"/api/albums/{album['id']}/photos",
        files={"file": ("x.png", _png_bytes(), "image/png")},
        data={"upload_id": "not-a-uuid"},
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["field"] == "upload_id"

    # 缺文件
    resp = await a.post(
        f"/api/albums/{album['id']}/photos",
        data={"upload_id": str(uuid.uuid4())},
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["field"] == "file"

    # 恰好 10,000,000 字节的合规 PNG 通过大小检查
    exact = _png_padded_to(10_000_000)
    assert len(exact) == 10_000_000
    resp = await a.post(
        f"/api/albums/{album['id']}/photos",
        files={"file": ("exact.png", exact, "image/png")},
        data={"upload_id": str(uuid.uuid4())},
    )
    assert resp.status_code == 201, resp.text


async def test_write_origin_check(client: AsyncClient, users):
    a = await users("org")
    category_id = await _get_category_id(a, "生活")
    resp = await a.post(
        "/api/albums",
        json={"name": "来源校验", "category_id": category_id, "visibility": "public"},
        headers={"origin": "http://evil.example"},
    )
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "ORIGIN_FORBIDDEN"


async def test_guest_requires_auth(client: AsyncClient):
    resp = await client.get("/api/albums")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "AUTH_REQUIRED"
