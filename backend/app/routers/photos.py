"""照片路由：上传、相册照片列表、详情与原图 / 缩略图读取。"""
from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..deps import check_write_origin, get_current_user, get_db, require_member
from ..errors import ApiError
from ..models import User
from ..schemas import parse_upload_id
from ..services.photos import PhotoService, photo_to_view

router = APIRouter(tags=["photos"])
service = PhotoService()


@router.post(
    "/albums/{album_id}/photos",
    status_code=201,
    dependencies=[Depends(check_write_origin)],
)
async def upload_photo(
    album_id: int,
    file: UploadFile | None = File(None),
    upload_id: str | None = Form(None),
    user: User = Depends(require_member),
    session: Session = Depends(get_db),
):
    if file is None or not file.filename:
        raise ApiError(422, "VALIDATION_ERROR", "缺少图片文件", field="file")
    parsed_upload_id = parse_upload_id(upload_id)
    data = await file.read()
    result = service.upload(session, user, album_id, data, parsed_upload_id)
    return JSONResponse(
        status_code=201 if result.created else 200,
        content=photo_to_view(result.photo).model_dump(mode="json"),
    )


@router.get("/albums/{album_id}/photos")
def list_photos(
    album_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    photos = service.list_photos(session, user, album_id)
    return {"items": [photo_to_view(p).model_dump(mode="json") for p in photos]}


@router.get("/photos/{photo_id}")
def photo_detail(
    photo_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    return service.get_detail(session, user, photo_id)


@router.get("/photos/{photo_id}/original")
def photo_original(
    photo_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    return service.open_image(session, user, photo_id, "original")


@router.get("/photos/{photo_id}/thumbnail")
def photo_thumbnail(
    photo_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    return service.open_image(session, user, photo_id, "thumbnail")
