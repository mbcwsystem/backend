from datetime import date, datetime

from fastapi import HTTPException
from sqlalchemy import and_, exists, func
from sqlalchemy.orm import Session, joinedload

from app.core.pagination import paginate
from app.modules.auth.models import User
from app.modules.community.models import CategoryEnum, Comment, CommentLike, Post
from app.modules.community.permissions import (
    can_delete_comment,
    can_delete_post,
    can_update_comment,
    can_update_post,
    can_write_comment,
    can_write_post,
)
from app.modules.community.schemas import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
    PaginatedResponse,
    PostCreate,
    PostListResponse,
    PostResponse,
    PostUpdate,
)


# 카테고리 -----
def get_category_post_counts(db: Session, category: CategoryEnum | None = None) -> int:
    """
    카테고리 별 게시글 수 조회
    - category=None이면 전체 게시글 수 반환
    """
    query = db.query(func.count(Post.id))
    if category:
        query = query.filter(Post.category == category)
    return query.scalar()


def get_all_category_post_counts(db: Session) -> dict[str, int]:
    """
    모든 카테고리별 게시글 수 반환
    """
    counts = {}
    total = 0
    for cat in CategoryEnum:
        cat_count = get_category_post_counts(db, cat)
        counts[cat.value] = cat_count
        total += cat_count
    counts["전체"] = total
    return counts


# 게시글 -----
def create_post(db: Session, user, data: PostCreate) -> PostResponse:
    """
    게시글 생성
    - 자유게시판: 모두(출근용 제외)
    - 공지: 관리자
    - 교대(대타)/휴무: 자동생성(사용자x)
    """

    # 권한체크
    if not can_write_post(user, data.category):
        raise HTTPException(403, "게시글 작성 권한이 없습니다.")

    # 시스템 생성(근무교대, 휴무신청) 카테고리에 작성 금지
    if data.category in (CategoryEnum.shift, CategoryEnum.dayoff):
        raise HTTPException(400, "이 카테고리는 사용자가 작성할 수 없습니다.")

    post = Post(
        title=data.title,
        content=data.content,
        category=data.category,
        author_id=user.id,
        system_generated=False,  # shift/dayoff만 True
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return _build_post_response(db, post)


def get_post(db: Session, post_id: int, user) -> PostResponse:
    """
    게시글 상세 조회 (댓글 제외)
    """
    post = (
        db.query(Post)
        .options(joinedload(Post.author))
        .filter(Post.id == post_id)
        .first()
    )

    if not post:
        raise HTTPException(404, "게시글을 찾을 수 없습니다.")

    return _build_post_response(db, post)


def list_posts(
    db: Session,
    user,
    category: CategoryEnum | None = None,
    author_id: int | None = None,
    page: int = 1,
    page_size: int = 5,
    search: str | None = None,
    search_scope: str = "all",
    order_by: str = "latest",
    from_date: date | None = None,
    to_date: date | None = None,
) -> PaginatedResponse[PostListResponse]:
    """
    게시글 목록 조회
    - 필터링 (내가 쓴 글, 카테고리, 날짜 범위)
    - 검색 (제목, 내용, 작성자 이름) 범위 지정 가능
    - 정렬 옵션(최신순, 오래된 순, 인기순 / 디폴트: 최신순 정렬)
    - 페이지네이션 적용(기본 1페이지, 5개씩 보기)
    """
    query = db.query(Post).options(joinedload(Post.author))

    # 내가 쓴 글 필터
    if author_id:
        query = query.filter(Post.author_id == author_id)

    # 카테고리 필터
    if category:
        query = query.filter(Post.category == category)

    # 검색
    if search:
        search_pattern = f"%{search}%"

        if search_scope == "all":
            query = query.join(Post.author).filter(
                (Post.title.ilike(search_pattern))
                | (Post.content.ilike(search_pattern))
                | (User.name.ilike(search_pattern))
            )
        elif search_scope == "title":
            query = query.filter(Post.title.ilike(search_pattern))
        elif search_scope == "content":
            query = query.filter(Post.content.ilike(search_pattern))
        elif search_scope == "author":
            query = query.join(Post.author).filter(User.name.ilike(search_pattern))

    # 날짜 필터
    if from_date:
        query = query.filter(Post.created_at >= from_date)

    if to_date:
        # to_date의 23:59:59까지 포함
        to_datetime = datetime.combine(to_date, datetime.max.time())
        query = query.filter(Post.created_at <= to_datetime)

    # 정렬
    if order_by == "latest":
        query = query.order_by(Post.created_at.desc())
    elif order_by == "oldest":
        query = query.order_by(Post.created_at.asc())
    elif order_by == "popular":
        # 댓글 수 기준 정렬 (subquery 사용)
        comment_count = (
            db.query(Comment.post_id, func.count(Comment.id).label("count"))
            .group_by(Comment.post_id)
            .subquery()
        )
        query = query.outerjoin(
            comment_count, Post.id == comment_count.c.post_id
        ).order_by(
            func.coalesce(comment_count.c.count, 0).desc(), Post.created_at.desc()
        )

    return paginate(query, page, page_size, lambda p: _build_post_list_response(db, p))


def update_post(db: Session, user, post_id: int, data: PostUpdate) -> PostResponse:
    """
    게시글 수정
    """
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(404, "게시글이 존재하지 않습니다.")

    if not can_update_post(user, post.author_id):
        raise HTTPException(403, "게시글 수정 권한이 없습니다.")

    # 필드 업데이트
    if data.title is not None:
        post.title = data.title

    if data.content is not None:
        post.content = data.content

    db.commit()
    db.expire(post)  # 세션 캐시 무효화

    return _build_post_response(db, post)


def delete_post(db: Session, user, post_id: int):
    """
    게시글 삭제
    - 작성자 또는 관리자만 삭제 가능
    - notice/shift/dayoff는 관리자만 삭제 가능
    """
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(404, "게시글이 존재하지 않습니다.")

    if not can_delete_post(user, post.author_id, post.category):
        raise HTTPException(403, "게시글 삭제 권한이 없습니다.")

    db.delete(post)
    db.commit()

    return {"message": "게시글이 삭제되었습니다."}


# 댓글 -----
def create_comment(
    db: Session, user, post_id: int, data: CommentCreate
) -> CommentResponse:
    """
    댓글 작성
    - 출근용 제외 모두
    """
    if not can_write_comment(user):
        raise HTTPException(403, "댓글 작성 권한이 없습니다.")

    post = db.query(exists().where(Post.id == post_id)).scalar()
    if not post:
        raise HTTPException(404, "게시글을 찾을 수 없습니다.")

    comment = Comment(post_id=post_id, author_id=user.id, content=data.content)

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return _build_comment_response(db, comment, user)


def list_comments(db: Session, user, post_id: int, page: int = 1, page_size: int = 10):
    query = (
        db.query(Comment)
        .options(joinedload(Comment.author))
        .filter(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
    )

    return paginate(
        query, page, page_size, lambda c: _build_comment_response(db, c, user)
    )


def update_comment(
    db: Session, user, comment_id: int, data: CommentUpdate
) -> CommentResponse:
    """
    댓글 수정
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(404, "댓글이 존재하지 않습니다.")

    if not can_update_comment(user, comment.author_id):
        raise HTTPException(403, "댓글 수정 권한이 없습니다.")

    if data.content is not None:
        comment.content = data.content

    db.commit()

    db.expire(comment)  # 세션 캐시 무효화
    # author 관계까지 포함해서 재조회
    comment = (
        db.query(Comment)
        .options(joinedload(Comment.author))
        .filter(Comment.id == comment_id)
        .first()
    )

    return _build_comment_response(db, comment, user)


def delete_comment(db: Session, user, comment_id: int):
    """
    댓글 삭제
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(404, "댓글이 존재하지 않습니다.")

    if not can_delete_comment(user, comment.author_id):
        raise HTTPException(403, "댓글 삭제 권한이 없습니다.")

    db.delete(comment)
    db.commit()

    return {"message": "댓글이 삭제되었습니다."}


def toggle_comment_like(db: Session, user, comment_id: int):
    existing = (
        db.query(CommentLike)
        .filter(CommentLike.comment_id == comment_id, CommentLike.user_id == user.id)
        .first()
    )
    if existing:
        db.delete(existing)
        is_liked = False
    else:
        db.add(CommentLike(comment_id=comment_id, user_id=user.id))
        is_liked = True
    db.commit()
    count = (
        db.query(func.count(CommentLike.id))
        .filter(CommentLike.comment_id == comment_id)
        .scalar()
    )
    return {"is_liked": is_liked, "like_count": count}


# sqlalchemy Post -> pydantic PostResponse (응답 스키마 변환) -----
def _build_post_list_response(db: Session, post: Post, user=None) -> PostListResponse:
    # 댓글 개수 계산
    comments_count = (
        db.query(func.count(Comment.id)).filter(Comment.post_id == post.id).scalar()
    )

    return PostListResponse(
        id=post.id,
        category=post.category,
        title=post.title,
        content=post.content,
        author_id=post.author_id,
        author_name=post.author.name,
        author_position=post.author.position,
        created_at=post.created_at,
        updated_at=post.updated_at,
        comments_count=comments_count,
    )


def _build_post_response(db: Session, post: Post) -> PostResponse:
    # 상세 조회용 (댓글 리스트 제외, 개수만 포함)
    comments_count = (
        db.query(func.count(Comment.id)).filter(Comment.post_id == post.id).scalar()
    )

    return PostResponse(
        id=post.id,
        category=post.category,
        title=post.title,
        content=post.content,
        author_id=post.author_id,
        author_name=post.author.name,
        author_position=post.author.position,
        system_generated=post.system_generated,
        created_at=post.created_at,
        updated_at=post.updated_at,
        comments_count=comments_count,
    )


def _build_comment_response(
    db: Session, comment: Comment, user=None
) -> CommentResponse:
    # 1. 좋아요 개수 계산
    like_count = (
        db.query(func.count(CommentLike.id))
        .filter(CommentLike.comment_id == comment.id)
        .scalar()
    )

    # 2. 유저가 좋아요 눌렀는지 확인
    is_liked = False
    if user:
        is_liked = db.query(
            exists().where(
                and_(
                    CommentLike.comment_id == comment.id, CommentLike.user_id == user.id
                )
            )
        ).scalar()

    return CommentResponse(
        id=comment.id,
        post_id=comment.post_id,
        author_id=comment.author_id,
        author_name=comment.author.name,
        author_position=comment.author.position,
        content=comment.content,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        like_count=like_count,
        is_liked=is_liked,
    )
