from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.community import services
from app.modules.community.models import CategoryEnum
from app.modules.community.schemas import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
    PostCreate,
    PostResponse,
    PostUpdate,
)
from app.utils.permission_utils import is_system

router = APIRouter()


# 출근용 계정 차단
def get_community_user(user=Depends(get_current_user)):
    if is_system(user):
        raise HTTPException(403, "출근용 계정은 커뮤니티 기능을 사용할 수 없습니다.")
    return user


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
    return services.create_post(db, user, data)


@router.get("/posts", response_model=list[PostResponse], summary="게시글 목록 조회")
def list_posts(
    category: Optional[CategoryEnum] = None,
    db: Session = Depends(get_db),
    user=Depends(get_community_user),
):
    return services.list_posts(db, category)


@router.get("/posts/{post_id}", response_model=PostResponse, summary="게시글 상세 조회")
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_community_user),
):
    return services.get_post(db, post_id)


@router.patch("/posts/{post_id}", response_model=PostResponse, summary="게시글 수정")
def update_post(
    post_id: int,
    data: PostUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_community_user),
):
    return services.update_post(db, user, post_id, data)


@router.delete("/posts/{post_id}", summary="게시글 삭제")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_community_user),
):
    return services.delete_post(db, user, post_id)


# 댓글 API -----
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
    return services.update_comment(db, user, comment_id, data)


@router.delete("/comments/{comment_id}", summary="댓글 삭제")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_community_user),
):
    return services.delete_comment(db, user, comment_id)
