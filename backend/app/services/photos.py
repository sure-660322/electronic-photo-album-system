"""照片服务：上传（校验、原图保存、缩略图生成、事务与重试）、列表、详情与图片读取。"""
import io
import uuid
from dataclasses import dataclass

from fastapi.responses import FileResponse
from PIL import Image
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session, selectinload

from ..errors import ApiError
from ..models import Comment, Photo, PhotoLike, User
from ..schemas import CommentOut, LikeStateOut, PhotoDetailOut, PhotoOut
from .albums import AlbumAccessPolicy
from .storage import LocalPhotoStorage

MAX_SIZE_BYTES = 10_000_000
THUMBNAIL_LONG_EDGE = 320
ALLOWED_FORMATS = {
    "JPEG": ("jpg", "image/jpeg"),
    "PNG": ("png", "image/png"),
    "GIF": ("gif", "image/gif"),
}


@dataclass
class UploadResult:
    photo: Photo
    created: bool


class PhotoService:
    def __init__(
        self,
        policy: AlbumAccessPolicy | None = None,
        storage: LocalPhotoStorage | None = None,
    ):
        self.policy = policy or AlbumAccessPolicy()
        self.storage = storage or LocalPhotoStorage()

    # ---- 上传 ----

    def upload(
        self, session: Session, actor: User, album_id: int,
        data: bytes, upload_id: uuid.UUID,
    ) -> UploadResult:
        self.policy.require_owned(session, actor, album_id)

        if len(data) > MAX_SIZE_BYTES:
            raise ApiError(413, "IMAGE_TOO_LARGE", "图片超过 10 MB 上限", field="file")
        if len(data) == 0:
            raise ApiError(422, "INVALID_IMAGE", "图片内容为空", field="file")

        ext, media_type = self._validate_image(data)

        # 本次尝试独立目录；重试沿用 upload_id 命中已提交记录时不再写文件。
        file_key = uuid.uuid4().hex
        relative_dir = f"albums/{album_id}/{file_key}"
        original_rel = f"{relative_dir}/original.{ext}"
        thumbnail_rel = f"{relative_dir}/thumbnail.png"

        stmt = (
            pg_insert(Photo)
            .values(
                album_id=album_id,
                uploader_id=actor.id,
                original_path=original_rel,
                thumbnail_path=thumbnail_rel,
                upload_id=upload_id,
                media_type=media_type,
                size_bytes=len(data),
            )
            .on_conflict_do_nothing(
                index_elements=["album_id", "uploader_id", "upload_id"]
            )
            .returning(Photo.id)
        )
        inserted_id = session.execute(stmt).scalar_one_or_none()
        if inserted_id is None:
            # 同一 upload_id 已提交过：读取既有照片直接返回（幂等重试）。
            session.rollback()
            existing = self._load_photo(session, triple=(album_id, actor.id, upload_id))
            return UploadResult(existing, False)

        thumbnail = self._build_thumbnail(data)
        try:
            self.storage.save(original_rel, data)
            self.storage.save(thumbnail_rel, thumbnail)
        except Exception:
            session.rollback()
            self.storage.remove_dir(relative_dir)
            raise ApiError(500, "UPLOAD_FAILED", "上传失败，请重试")

        try:
            session.commit()
        except Exception:
            try:
                session.rollback()
            except Exception:
                # 回滚也失败时提交结果未知：保留文件，客户端按原 upload_id 重试。
                raise ApiError(
                    503, "UPLOAD_STATUS_UNKNOWN", "上传结果暂时无法确认，请重试"
                )
            self.storage.remove_dir(relative_dir)
            raise ApiError(500, "UPLOAD_FAILED", "上传失败，请重试")

        return UploadResult(self._load_photo(session, photo_id=inserted_id), True)

    def _validate_image(self, data: bytes) -> tuple[str, str]:
        """解码识别 JPEG/PNG/GIF；无法解码或格式不符按 INVALID_IMAGE 返回。"""
        try:
            with Image.open(io.BytesIO(data)) as image:
                image_format = image.format
                image.verify()
        except Exception:
            raise ApiError(422, "INVALID_IMAGE", "图片内容无法解码", field="file")
        if image_format not in ALLOWED_FORMATS:
            raise ApiError(
                422, "INVALID_IMAGE", "仅支持 jpg/png/gif 图片", field="file"
            )
        ext, media_type = ALLOWED_FORMATS[image_format]
        return ext, media_type

    def _build_thumbnail(self, data: bytes) -> bytes:
        """等比缩放至最长边不超过 320 像素的 PNG 缩略图，GIF 取首帧。"""
        image = Image.open(io.BytesIO(data))
        if image.mode == "P":
            has_alpha = "transparency" in image.info
            image = image.convert("RGBA" if has_alpha else "RGB")
        elif image.mode not in ("RGB", "RGBA", "L"):
            image = image.convert("RGB")
        image.thumbnail(
            (THUMBNAIL_LONG_EDGE, THUMBNAIL_LONG_EDGE), Image.Resampling.LANCZOS
        )
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    # ---- 浏览 ----

    def list_photos(self, session: Session, actor: User, album_id: int) -> list[Photo]:
        self.policy.require_visible(session, actor, album_id)
        query = (
            select(Photo)
            .options(selectinload(Photo.uploader))
            .where(Photo.album_id == album_id)
            .order_by(Photo.id.desc())
        )
        return list(session.scalars(query))

    def get_detail(self, session: Session, actor: User, photo_id: int) -> PhotoDetailOut:
        photo = self._require_photo(session, actor, photo_id)
        comments = list(
            session.scalars(
                select(Comment)
                .options(selectinload(Comment.author))
                .where(Comment.photo_id == photo_id)
                .order_by(Comment.created_at.desc(), Comment.id.desc())
            )
        )
        like_count = session.scalar(
            select(func.count()).select_from(PhotoLike)
            .where(PhotoLike.photo_id == photo_id)
        )
        liked = session.scalar(
            select(func.count()).select_from(PhotoLike).where(
                PhotoLike.photo_id == photo_id, PhotoLike.user_id == actor.id
            )
        )
        return PhotoDetailOut(
            photo=photo_to_view(photo),
            original_url=f"/api/photos/{photo.id}/original",
            comments=[
                CommentOut(
                    id=c.id,
                    photo_id=c.photo_id,
                    author={"id": c.author.id, "username": c.author.username},
                    body=c.body,
                    created_at=c.created_at,
                )
                for c in comments
            ],
            like=LikeStateOut(liked=bool(liked), like_count=int(like_count or 0)),
        )

    def open_image(self, session: Session, actor: User, photo_id: int, variant: str):
        """原图 / 缩略图读取：每次请求独立校验会话与相册可见性。"""
        photo = self._require_photo(session, actor, photo_id)
        if variant == "original":
            relative = photo.original_path
            media_type = photo.media_type
        else:
            relative = photo.thumbnail_path
            media_type = "image/png"
        if not self.storage.exists(relative):
            raise ApiError(404, "PHOTO_UNAVAILABLE", "照片不可访问")
        return FileResponse(
            self.storage.resolve(relative),
            media_type=media_type,
            headers={"Cache-Control": "no-store"},
        )

    def _require_photo(self, session: Session, actor: User, photo_id: int) -> Photo:
        photo = self._load_photo(session, photo_id=photo_id)
        if photo is None:
            raise ApiError(404, "PHOTO_UNAVAILABLE", "照片不可访问")
        album = self.policy.require_visible(session, actor, photo.album_id)
        photo.album = album
        return photo

    def _load_photo(
        self,
        session: Session,
        photo_id: int | None = None,
        triple: tuple[int, int, uuid.UUID] | None = None,
    ) -> Photo | None:
        query = select(Photo).options(
            selectinload(Photo.uploader), selectinload(Photo.album)
        )
        if photo_id is not None:
            query = query.where(Photo.id == photo_id)
        else:
            album_id, uploader_id, upload_id = triple
            query = query.where(
                Photo.album_id == album_id,
                Photo.uploader_id == uploader_id,
                Photo.upload_id == upload_id,
            )
        return session.scalar(query)


def photo_to_view(photo: Photo) -> PhotoOut:
    return PhotoOut(
        id=photo.id,
        album_id=photo.album_id,
        uploader={"id": photo.uploader.id, "username": photo.uploader.username},
        created_at=photo.created_at,
        thumbnail_url=f"/api/photos/{photo.id}/thumbnail",
    )
