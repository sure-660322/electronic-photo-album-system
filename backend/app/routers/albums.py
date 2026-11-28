"""相册路由：列表（visible/mine）、单条、创建与乐观锁修改。"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..deps import check_write_origin, get_current_user, get_db, require_member
from ..models import Album, User
from ..schemas import AlbumCreateIn, AlbumOut, AlbumUpdateIn
from ..services.albums import AlbumService

router = APIRouter(prefix="/albums", tags=["albums"])
service = AlbumService()


def album_to_view(album: Album) -> AlbumOut:
    return AlbumOut(
        id=album.id,
        name=album.name,
        visibility=album.visibility,
        version=album.version,
        owner_id=album.owner_id,
        category={"id": album.category.id, "name": album.category.name},
        created_at=album.created_at,
        updated_at=album.updated_at,
    )


@router.get("")
def list_albums(
    scope: str = Query("visible", pattern="^(visible|mine)$"),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    albums = service.list_albums(session, user, scope)
    return {"items": [album_to_view(a) for a in albums]}


@router.post("", status_code=201, dependencies=[Depends(check_write_origin)])
def create_album(
    data: AlbumCreateIn,
    user: User = Depends(require_member),
    session: Session = Depends(get_db),
):
    album = service.create(session, user, data)
    return album_to_view(album)


@router.get("/{album_id}")
def get_album(
    album_id: int,
    scope: str = Query("visible", pattern="^(visible|mine)$"),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    album = service.get_album(session, user, album_id, scope)
    return album_to_view(album)


@router.put("/{album_id}", dependencies=[Depends(check_write_origin)])
def update_album(
    album_id: int,
    data: AlbumUpdateIn,
    user: User = Depends(require_member),
    session: Session = Depends(get_db),
):
    album = service.update(session, user, album_id, data)
    return album_to_view(album)
