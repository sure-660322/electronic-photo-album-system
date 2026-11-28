"""相册服务与访问策略：可见性、归属、乐观锁更新（创建/修改相册设计 03/04）。"""
from datetime import datetime, timezone

from sqlalchemy import or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from ..errors import ApiError
from ..models import Album, Category, User
from ..schemas import AlbumCreateIn, AlbumUpdateIn


class AlbumAccessPolicy:
    """相册可见性与归属的统一判断，照片与评论模块复用。"""

    def require_visible(self, session: Session, actor: User, album_id: int) -> Album:
        album = self.load(session, album_id)
        if album is None or not album.visible_to(actor):
            raise ApiError(404, "ALBUM_UNAVAILABLE", "相册不可访问")
        return album

    def require_owned(self, session: Session, actor: User, album_id: int) -> Album:
        album = self.load(session, album_id)
        if album is None or album.owner_id != actor.id:
            raise ApiError(404, "ALBUM_UNAVAILABLE", "相册不存在或无权访问")
        return album

    def load(self, session: Session, album_id: int) -> Album | None:
        return session.scalar(
            select(Album)
            .options(selectinload(Album.category))
            .where(Album.id == album_id)
        )


class AlbumService:
    def __init__(self, policy: AlbumAccessPolicy | None = None):
        self.policy = policy or AlbumAccessPolicy()

    def list_albums(self, session: Session, actor: User, scope: str) -> list[Album]:
        query = (
            select(Album)
            .options(selectinload(Album.category))
            .order_by(Album.id.desc())
        )
        if scope == "mine":
            query = query.where(Album.owner_id == actor.id)
        else:
            # 可见范围 = 所有公开相册 + 本人全部相册。
            query = query.where(
                or_(Album.visibility == "public", Album.owner_id == actor.id)
            )
        return list(session.scalars(query))

    def get_album(
        self, session: Session, actor: User, album_id: int, scope: str
    ) -> Album:
        if scope == "mine":
            return self.policy.require_owned(session, actor, album_id)
        return self.policy.require_visible(session, actor, album_id)

    def create(self, session: Session, actor: User, data: AlbumCreateIn) -> Album:
        self._require_category(session, data.category_id)
        album = Album(
            owner_id=actor.id,
            category_id=data.category_id,
            name=data.name,
            visibility=data.visibility,
        )
        session.add(album)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ApiError(409, "CATEGORY_UNAVAILABLE", "所选类别已失效")
        session.refresh(album)
        return album

    def update(
        self, session: Session, actor: User, album_id: int, data: AlbumUpdateIn
    ) -> Album:
        # 先确认归属，404 与版本冲突分开处理。
        self.policy.require_owned(session, actor, album_id)
        self._require_category(session, data.category_id)
        result = session.execute(
            update(Album)
            .where(
                Album.id == album_id,
                Album.owner_id == actor.id,
                Album.version == data.version,
            )
            .values(
                name=data.name,
                category_id=data.category_id,
                visibility=data.visibility,
                version=data.version + 1,
                updated_at=datetime.now(timezone.utc),
            )
        )
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ApiError(409, "CATEGORY_UNAVAILABLE", "所选类别已失效")
        if result.rowcount == 0:
            still_owned = session.scalar(
                select(Album).where(
                    Album.id == album_id, Album.owner_id == actor.id
                )
            )
            if still_owned is None:
                raise ApiError(404, "ALBUM_UNAVAILABLE", "相册不存在或无权修改")
            raise ApiError(409, "ALBUM_VERSION_CONFLICT", "相册已被他人修改，请重新载入")
        return self.policy.load(session, album_id)

    def _require_category(self, session: Session, category_id: int) -> None:
        if session.get(Category, category_id) is None:
            raise ApiError(
                409, "CATEGORY_UNAVAILABLE", "所选类别已失效", field="category_id"
            )
