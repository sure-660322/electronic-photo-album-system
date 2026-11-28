"""类别路由：主流程仅提供类别列表供相册表单下拉框使用。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..deps import get_current_user, get_db
from ..models import Category, User
from ..schemas import CategoryOut
from ..services.categories import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])
service = CategoryService()


@router.get("")
def list_categories(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    items = service.list_categories(session)
    return {"items": [CategoryOut(id=c.id, name=c.name) for c in items]}
