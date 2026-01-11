import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base

# SQLite 메모리 DB
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    """테스트용 DB 엔진 생성, 세션 전체에서 공유"""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)  # 테이블 생성
    yield engine
    Base.metadata.drop_all(engine)  # 테스트 종료 후 테이블 제거


@pytest.fixture(scope="function")
def db(engine):
    """
    트랜잭션 기반 세션 제공
    테스트 함수마다 롤백됨
    """
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session  # 테스트 코드에서 session 사용

    session.close()
    transaction.rollback()
    connection.close()
