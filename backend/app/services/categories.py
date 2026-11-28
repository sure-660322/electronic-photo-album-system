"""类别服务：本轮主流程只提供类别列表（类别管理属管理员模块）。"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Category


class CategoryService:
    def list_categories(self, session: Session) -> list[Category]:
        return list(session.scalars(select(Category).order_by(Category.id.asc())))
