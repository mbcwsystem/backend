from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.config import settings
from app.core.database import Base


class CategoryEnum(str, PyEnum):
    notice = "공지"
    shift = "근무교대"
    dayoff = "휴무신청"
    free_board = "자유게시판"


class Post(Base):
    __tablename__ = "community_post"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(
        Enum(CategoryEnum),
        nullable=False,
        comment="공지, 근무교대, 휴무신청, 자유게시판",
    )
    title = Column(String(255), nullable=False, comment="제목")
    content = Column(Text, nullable=False, comment="내용")
    author_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, comment="작성자 id"
    )
    system_generated = Column(
        Boolean, nullable=False, default=False, comment="시스템 자동생성 여부"
    )

    shift_request = relationship(
        "ShiftRequest",
        back_populates="post",
        uselist=False,
        primaryjoin="Post.id==foreign(ShiftRequest.generated_post_id)",
        viewonly=True,
    )

    dayoff_request = relationship(
        "DayoffRequest",
        back_populates="post",
        uselist=False,
        primaryjoin="Post.id==foreign(DayoffRequest.generated_post_id)",
        viewonly=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=settings.now_kst,
        comment="작성일시",
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=settings.now_kst,
        onupdate=settings.now_kst,
        comment="수정일시",
    )

    author = relationship("User", back_populates="posts")

    comments = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self):
        short_title = (
            self.title[:20] + "..."
            if self.title and len(self.title) > 20
            else self.title
        )
        return (
            f"[CommunityPost] id={self.id}, category={self.category.value}, "
            f"title={short_title}, author_id={self.author_id}, "
            f"system_generated={self.system_generated}"
        )


class Comment(Base):
    __tablename__ = "community_comment"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(
        Integer,
        ForeignKey("community_post.id"),
        nullable=False,
        comment="대상 게시글 id",
    )
    author_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, comment="작성자 id"
    )
    content = Column(Text, nullable=False, comment="내용")
    created_at = Column(DateTime, nullable=False, default=settings.now_kst)
    updated_at = Column(
        DateTime, nullable=False, default=settings.now_kst, onupdate=settings.now_kst
    )

    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")

    def __repr__(self):
        short_content = (
            self.content[:20] + "..."
            if self.content and len(self.content) > 20
            else self.content
        )
        return (
            f"[CommunityComment] id={self.id}, post_id={self.post_id}, "
            f"author_id={self.author_id}, content={short_content}"
        )
