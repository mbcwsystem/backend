from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.community import services
from app.modules.community.models import CategoryEnum
from app.modules.community.schemas import (
    CategoryCountResponse,
    CommentCreate,
    CommentResponse,
    CommentUpdate,
    OrderBy,
    PaginatedResponse,
    PaginationParams,
    PostCreate,
    PostListResponse,
    PostResponse,
    PostUpdate,
    SearchScope,
)
from app.modules.community.services import (
    get_all_category_post_counts,
    get_category_post_counts,
)
from app.utils.permission_utils import is_system

router = APIRouter()


# 출근용 계정 차단
def get_community_user(user=Depends(get_current_user)):
    if is_system(user):
        raise HTTPException(403, "출근용 계정은 커뮤니티 기능을 사용할 수 없습니다.")
    return user


# 카테고리별 게시글 수 API -----
@router.get(
    "/category-counts",
    response_model=CategoryCountResponse,
    status_code=200,
    summary="카테고리별 게시글 수",
)
def category_counts(
    db: Session = Depends(get_db),
    category: str | None = Query(
        None, description="카테고리 이름 (공지, 근무교대, 휴무신청, 자유게시판)"
    ),
    user=Depends(get_community_user),
) -> CategoryCountResponse:
    """
    전체 또는 카테고리별 게시글 수 조회
    - category 파라미터 없으면 전체 + 각 카테고리 count 반환
    - category 파라미터 있으면 해당 카테고리 count만 반환
    """
    if category:
        try:
            cat_enum = CategoryEnum(category)
        except ValueError:
            return {"counts": {category: 0}}  # 존재하지 않는 카테고리 0

        count = get_category_post_counts(db, cat_enum)
        return {"counts": {category: count}}

    # 전체 + 카테고리별
    counts = get_all_category_post_counts(db)
    return {"counts": counts}


# 게시글 API -----
@router.post(
    "/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="게시글 생성",
)
def create_post(
    data: PostCreate,
    db: Session = Depends(get_db),
    user=Depends(get_community_user),
):
    """
    게시글 생성
    - 자유게시판: 모두(출근용 제외)
    - 공지: 관리자
    - 교대(대타)/휴무: 자동생성(사용자x)
    """

    return services.create_post(db, user, data)


@router.get(
    "/posts",
    response_model=PaginatedResponse[PostListResponse],
    summary="게시글 목록 조회",
)
def list_posts(
    mine: bool = Query(False, description="내가 쓴 글만 보기"),
    category: CategoryEnum | None = Query(None, description="카테고리 필터"),
    search_scope: SearchScope = Query(SearchScope.all, description="검색 범위"),
    search: str | None = Query(None, description="검색어"),
    order_by: OrderBy = Query(OrderBy.latest, description="정렬 기준"),
    from_date: date | None = Query(
        None, description="작성일이 해당 날짜 이후인 게시글 검색 (YYYY-MM-DD)"
    ),
    to_date: date | None = Query(
        None, description="작성일이 해당 날짜까지인 게시글 검색(YYYY-MM-DD)"
    ),
    db: Session = Depends(get_db),
    user=Depends(get_community_user),
    pagination: PaginationParams = Depends(),
):
    """
    게시글 목록 조회
    - 필터링 (내가 쓴 글, 카테고리, 날짜 범위)
    - 검색 (제목, 내용, 작성자 이름) 범위 지정 가능
    - 정렬 옵션(최신순, 오래된 순, 인기순 / 디폴트: 최신순 정렬)
    - 페이지네이션 적용(기본 1페이지, 5개씩 보기)
    """
    # mine이 True일 경우 현재 로그인한 user.id를 넘기고, False면 None을 넘김
    author_id = user.id if mine else None

    return services.list_posts(
        db=db,
        user=user,
        author_id=author_id,
        category=category,
        page=pagination.page,
        page_size=pagination.page_size,
        search=search,
        search_scope=search_scope.value,
        order_by=order_by.value,
        from_date=from_date,
        to_date=to_date,
    )


@router.get("/posts/{post_id}", response_model=PostResponse, summary="게시글 상세 조회")
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_community_user),
):
    """
    게시글 상세 조회 (댓글 제외)
    """
    return services.get_post(db, post_id, user)


@router.patch("/posts/{post_id}", response_model=PostResponse, summary="게시글 수정")
def update_post(
    post_id: int,
    data: PostUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_community_user),
):
    """
    게시글 수정
    """
    return services.update_post(db, user, post_id, data)


@router.delete("/posts/{post_id}", summary="게시글 삭제")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_community_user),
):
    """
    게시글 삭제
    - 작성자 또는 관리자만 삭제 가능
    - notice/shift/dayoff는 관리자만 삭제 가능
    """
    return services.delete_post(db, user, post_id)


# 댓글 API -----
@router.get(
    "/posts/{post_id}/comments",
    response_model=PaginatedResponse[CommentResponse],
    summary="댓글 목록 조회",
)
def list_comments(
    post_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_community_user),
    pagination: PaginationParams = Depends(),
):
    """
    특정 게시글의 댓글을 페이지네이션해서 조회 \n
    각 댓글마다 좋아요 수와 현재 유저의 좋아요 여부가 포함됨
    """
    return services.list_comments(
        db=db,
        user=user,
        post_id=post_id,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.post(
    "/posts/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="댓글 생성",
)
def create_comment(
    post_id: int,
    data: CommentCreate,
    db: Session = Depends(get_db),
    user=Depends(get_community_user),
):
    """
    댓글 작성
    - 출근용 제외 모두
    """
    return services.create_comment(db, user, post_id, data)


@router.patch(
    "/comments/{comment_id}", response_model=CommentResponse, summary="댓글 수정"
)
def update_comment(
    comment_id: int,
    data: CommentUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_community_user),
):
    """
    댓글 수정
    """
    return services.update_comment(db, user, comment_id, data)


@router.delete("/comments/{comment_id}", summary="댓글 삭제")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_community_user),
):
    """
    댓글 삭제
    """
    return services.delete_comment(db, user, comment_id)


@router.post("/comments/{comment_id}/like", summary="댓글 좋아요 토글")
def toggle_comment_like(
    comment_id: int, db: Session = Depends(get_db), user=Depends(get_community_user)
):
    """
    댓글에 좋아요를 누르거나 취소
    """
    return services.toggle_comment_like(db=db, user=user, comment_id=comment_id)
