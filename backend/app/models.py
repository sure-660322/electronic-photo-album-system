"""领域实体：与 docker/postgres/02-schema.sql 中的六张表一一对应。"""
import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True)
    email: Mapped[str] = mapped_column(String(254))
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    albums: Mapped[list["Album"]] = relationship(back_populates="owner")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    albums: Mapped[list["Album"]] = relationship(back_populates="category")


class Album(Base):
    __tablename__ = "albums"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    name: Mapped[str] = mapped_column(String(100))
    visibility: Mapped[str] = mapped_column(String(7))
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    owner: Mapped[User] = relationship(back_populates="albums")
    category: Mapped[Category] = relationship(back_populates="albums")
    photos: Mapped[list["Photo"]] = relationship(back_populates="album")

    def visible_to(self, user: "User") -> bool:
        return self.visibility == "public" or self.owner_id == user.id


class Photo(Base):
    __tablename__ = "photos"
    __table_args__ = (
        UniqueConstraint(
            "album_id", "uploader_id", "upload_id",
            name="photos_album_uploader_upload_key",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    album_id: Mapped[int] = mapped_column(ForeignKey("albums.id"))
    uploader_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    original_path: Mapped[str] = mapped_column(Text)
    thumbnail_path: Mapped[str] = mapped_column(Text)
    upload_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    media_type: Mapped[str] = mapped_column(String(32))
    size_bytes: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    album: Mapped[Album] = relationship(back_populates="photos")
    uploader: Mapped[User] = relationship()


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    photo_id: Mapped[int] = mapped_column(ForeignKey("photos.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    author: Mapped[User] = relationship()


class PhotoLike(Base):
    __tablename__ = "photo_likes"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), primary_key=True
    )
    photo_id: Mapped[int] = mapped_column(
        ForeignKey("photos.id"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
