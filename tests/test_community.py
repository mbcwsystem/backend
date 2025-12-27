import pytest
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

# 테스트용 Base
Base = declarative_base()

# -------------더미 모델 정의---------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(50), nullable=False)
    position = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)

    posts = relationship("Post", back_populates="author", cascade="all, delete")
    comments = relationship("Comment", back_populates="author", cascade="all, delete")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    content = Column(String(500))
    category = Column(String(50))
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete")
    system_generated = Column(Boolean, default=False)


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(500))
    post_id = Column(Integer, ForeignKey("posts.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")


# -------------테스트용 DB 설정----------------
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, echo=False)
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="function")
def db():
    """테스트용 DB 세션 + 매 테스트마다 초기화"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# --------------테스트용 데이터---------------
@pytest.fixture
def test_user(db):
    user = User(username="testuser", password="test", name="Test User", position="manager")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def post_data():
    return {"title": "초기 제목", "content": "초기 내용", "category": "free_board"}


@pytest.fixture
def comment_data():
    return {"content": "댓글 초기 내용"}


# --------------더미 서비스 함수---------------
def create_post(db, user, data):
    post = Post(title=data["title"], content=data["content"], category=data["category"], author=user)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def update_post(db, user, post_id, data):
    post = db.query(Post).filter(Post.id == post_id).first()
    post.title = data["title"]
    post.content = data["content"]
    db.commit()
    db.expire(post)  # 최신 DB 반영 위해 expire
    post = db.query(Post).filter(Post.id == post_id).first()
    return post


def create_comment(db, user, post_id, data):
    post = db.query(Post).filter(Post.id == post_id).first()
    comment = Comment(content=data["content"], author=user, post=post)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def update_comment(db, user, comment_id, data):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    comment.content = data["content"]
    db.commit()
    db.expire(comment)
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    return comment


# ---------------실제 테스트--------------
def test_update_post_print(db, test_user, post_data):
    post = create_post(db, test_user, post_data)
    print("\n\n원본 게시글:", post.title, post.content)

    updated_post = update_post(db, test_user, post.id, {"title": "수정 제목", "content": "수정 내용"})
    print("업데이트 후 게시글:", updated_post.title, updated_post.content)

    assert updated_post.title == "수정 제목"
    assert updated_post.content == "수정 내용"


def test_update_comment_print(db, test_user, post_data, comment_data):
    post = create_post(db, test_user, post_data)
    comment = create_comment(db, test_user, post.id, comment_data)
    print("\n\n원본 댓글:", comment.content)

    updated_comment = update_comment(db, test_user, comment.id, {"content": "댓글 수정 내용"})
    print("업데이트 후 댓글:", updated_comment.content)

    assert updated_comment.content == "댓글 수정 내용"
