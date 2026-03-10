import math
from typing import Any, Callable, TypeVar

from sqlalchemy.orm import Query

from app.modules.community.schemas import PaginatedResponse

T = TypeVar("T")


def paginate(
    query: Query,
    page: int,
    page_size: int,
    transform_fn: Callable[[Any], T] | None = None,
) -> PaginatedResponse[T]:
    """
    페이지네이션 함수
    """

    # 전체 개수
    total = query.count()

    # 전체 페이지 수
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    # offset, limit 적용
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    # 변환
    results = [transform_fn(item) for item in items] if transform_fn else items

    # previous / next 계산
    previous = page - 1 if page > 1 else None
    next_page = page + 1 if page < total_pages else None

    return PaginatedResponse(
        items=results,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        previous=previous,
        next=next_page,
    )
