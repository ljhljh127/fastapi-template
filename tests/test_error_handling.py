from collections.abc import Iterator

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.deps import get_db
from app.main import create_app

router = APIRouter(prefix="/boom", tags=["chassis"])


@router.get("")
def raise_unexpected_error() -> None:
    raise RuntimeError("boom")


def build_client(settings: Settings, db: Session) -> Iterator[TestClient]:
    application = create_app(settings)
    application.include_router(router, prefix=settings.api_v1_prefix)
    application.dependency_overrides[get_db] = lambda: db
    with TestClient(application, raise_server_exceptions=False) as client:
        yield client
    application.dependency_overrides.clear()


@pytest.fixture(name="boom_client")
def boom_client_fixture(settings: Settings, db: Session) -> Iterator[TestClient]:
    yield from build_client(settings, db)


@pytest.fixture(name="debug_boom_client")
def debug_boom_client_fixture(db: Session) -> Iterator[TestClient]:
    debug_settings = Settings(app_env="local", debug=True, log_level="CRITICAL", cors_origins=[])
    yield from build_client(debug_settings, db)


def test_unhandled_error_uses_error_envelope(boom_client: TestClient) -> None:
    response = boom_client.get("/api/v1/boom", headers={"X-Request-ID": "trace-1"})

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_error"
    assert response.json()["request_id"] == "trace-1"
    assert response.headers["X-Request-ID"] == "trace-1"


def test_debug_mode_does_not_leak_traceback(debug_boom_client: TestClient) -> None:
    response = debug_boom_client.get("/api/v1/boom")

    assert response.headers["content-type"].startswith("application/json")
    assert "Traceback" not in response.text
    assert response.json()["error"]["code"] == "internal_error"
