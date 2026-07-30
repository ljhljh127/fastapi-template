from collections.abc import Iterator

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.pagination import Page, PaginationDep, PaginationParams
from app.db.deps import get_db
from app.main import create_app

router = APIRouter(prefix="/items", tags=["chassis"])


@router.get("", response_model=Page[int])
def list_items(pagination: PaginationDep) -> Page[int]:
    items = list(range(pagination.offset, min(pagination.offset + pagination.limit, 45)))
    return Page.create(items, 45, pagination)


@pytest.fixture(name="page_client")
def page_client_fixture(settings: Settings, db: Session) -> Iterator[TestClient]:
    application = create_app(settings)
    application.include_router(router, prefix=settings.api_v1_prefix)
    application.dependency_overrides[get_db] = lambda: db
    with TestClient(application) as client:
        yield client
    application.dependency_overrides.clear()


def test_page_create_fills_envelope() -> None:
    params = PaginationParams(limit=10, offset=20)

    page = Page.create(["a", "b"], 42, params)

    assert page.items == ["a", "b"]
    assert page.total == 42
    assert page.limit == 10
    assert page.offset == 20


def test_params_reject_out_of_range_values() -> None:
    for kwargs in ({"limit": 0}, {"limit": 101}, {"offset": -1}):
        with pytest.raises(ValidationError):
            PaginationParams(**kwargs)


def test_defaults_apply_when_query_is_empty(page_client: TestClient) -> None:
    body = page_client.get("/api/v1/items").json()

    assert body["limit"] == 20
    assert body["offset"] == 0
    assert body["total"] == 45
    assert len(body["items"]) == 20


def test_limit_and_offset_come_from_query_string(page_client: TestClient) -> None:
    body = page_client.get("/api/v1/items", params={"limit": 5, "offset": 40}).json()

    assert body["items"] == [40, 41, 42, 43, 44]


def test_out_of_range_query_returns_422(page_client: TestClient) -> None:
    for params in ({"limit": 0}, {"limit": 101}, {"offset": -1}):
        response = page_client.get("/api/v1/items", params=params)

        assert response.status_code == 422, params
        assert response.json()["error"]["code"] == "validation_error"
