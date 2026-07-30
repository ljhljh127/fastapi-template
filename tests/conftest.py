from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import Settings
from app.db.deps import get_db
from app.db.registry import Base
from app.main import create_app


@pytest.fixture(name="settings")
def settings_fixture() -> Settings:
    return Settings(app_env="local", debug=False, log_level="WARNING", cors_origins=[])


@pytest.fixture(name="engine")
def engine_fixture() -> Iterator[Engine]:
    """StaticPool과 check_same_thread=False가 있어야 인메모리 DB를 TestClient 스레드와 공유한다."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(name="db")
def db_fixture(engine: Engine) -> Iterator[Session]:
    # 운영(session.py)과 같은 옵션을 쓴다. expire_on_commit을 다르게 주면
    # refresh 누락 같은 결함이 테스트에서만 안 보인다.
    with sessionmaker(bind=engine, autocommit=False, autoflush=False)() as session:
        yield session


@pytest.fixture(name="app")
def app_fixture(settings: Settings, db: Session) -> Iterator[FastAPI]:
    application = create_app(settings)
    application.dependency_overrides[get_db] = lambda: db
    yield application
    application.dependency_overrides.clear()


@pytest.fixture(name="client")
def client_fixture(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
