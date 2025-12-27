from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.modules.community.models import CategoryEnum, Comment, Post
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
    PostCreate,
    PostResponse,
    PostUpdate,
)


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

    return _build_post_response(post)


def get_post(db: Session, post_id: int) -> PostResponse:
    """
    게시글 상세 조회 (댓글포함)
    """
    post = (
        db.query(Post)
        .options(joinedload(Post.comments).joinedload(Comment.author))
        .filter(Post.id == post_id)
        .first()
    )

    if not post:
        raise HTTPException(404, "게시글을 찾을 수 없습니다.")

    return _build_post_response(post)


def list_posts(db: Session, category: CategoryEnum | None = None):
    """
    게시글 목록 조회
    - 카테고리별 필터링
    - 최신순 정렬
    """
    query = db.query(Post)

    if category:
        query = query.filter(Post.category == category)

    posts = query.order_by(Post.created_at.desc()).all()

    return [_build_post_response(p) for p in posts]


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

    # 관계까지 포함해서 재조회
    post = (
        db.query(Post)
        .options(joinedload(Post.comments).joinedload(Comment.author))
        .filter(Post.id == post_id)
        .first()
    )

    return _build_post_response(post)


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

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(404, "게시글을 찾을 수 없습니다.")

    comment = Comment(
        post_id=post.id,
        author_id=user.id,
        content=data.content,
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return _build_comment_response(comment)


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

    return _build_comment_response(comment)


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


# sqlalchemy Post -> pydantic PostResponse (응답 스키마 변환) -----
def _build_post_response(post: Post) -> PostResponse:
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
        comments=[_build_comment_response(c) for c in post.comments],
    )


def _build_comment_response(comment: Comment) -> CommentResponse:
    return CommentResponse(
        id=comment.id,
        post_id=comment.post_id,
        author_id=comment.author_id,
        author_name=comment.author.name,
        author_position=comment.author.position,
        content=comment.content,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
    )
