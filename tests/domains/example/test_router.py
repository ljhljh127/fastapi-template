from typing import Any

from fastapi.testclient import TestClient

BASE = "/api/v1/examples"


def create(client: TestClient, name: str = "alpha", **extra: object) -> dict[str, Any]:
    response = client.post(BASE, json={"name": name, **extra})
    assert response.status_code == 201, response.text
    body: dict[str, Any] = response.json()
    return body


def test_create_returns_created_resource(client: TestClient) -> None:
    body = create(client, "alpha", description="first")

    assert body["id"] > 0
    assert body["name"] == "alpha"
    assert body["description"] == "first"
    assert body["created_at"] is not None


def test_create_rejects_duplicate_name(client: TestClient) -> None:
    create(client, "alpha")

    response = client.post(BASE, json={"name": "alpha"})

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "example_name_conflict"


def test_create_rejects_blank_name(client: TestClient) -> None:
    response = client.post(BASE, json={"name": ""})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_get_returns_resource(client: TestClient) -> None:
    created = create(client, "alpha")

    response = client.get(f"{BASE}/{created['id']}")

    assert response.status_code == 200
    assert response.json()["name"] == "alpha"


def test_get_missing_returns_not_found(client: TestClient) -> None:
    response = client.get(f"{BASE}/9999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "example_not_found"
    assert response.json()["error"]["details"] == {"example_id": 9999}


def test_list_paginates(client: TestClient) -> None:
    for index in range(3):
        create(client, f"name-{index}")

    response = client.get(BASE, params={"limit": 2, "offset": 1})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert body["limit"] == 2
    assert body["offset"] == 1
    assert [item["name"] for item in body["items"]] == ["name-1", "name-2"]


def test_list_rejects_limit_above_maximum(client: TestClient) -> None:
    response = client.get(BASE, params={"limit": 1000})

    assert response.status_code == 422


def test_update_applies_partial_changes(client: TestClient) -> None:
    created = create(client, "alpha", description="first")

    response = client.patch(f"{BASE}/{created['id']}", json={"description": "second"})

    assert response.status_code == 200
    assert response.json()["name"] == "alpha"
    assert response.json()["description"] == "second"


def test_update_rejects_name_taken_by_another(client: TestClient) -> None:
    first = create(client, "alpha")
    create(client, "beta")

    response = client.patch(f"{BASE}/{first['id']}", json={"name": "beta"})

    assert response.status_code == 409


def test_update_allows_same_name(client: TestClient) -> None:
    created = create(client, "alpha")

    response = client.patch(f"{BASE}/{created['id']}", json={"name": "alpha"})

    assert response.status_code == 200


def test_delete_removes_resource(client: TestClient) -> None:
    created = create(client, "alpha")

    assert client.delete(f"{BASE}/{created['id']}").status_code == 204
    assert client.get(f"{BASE}/{created['id']}").status_code == 404


def test_delete_missing_returns_not_found(client: TestClient) -> None:
    assert client.delete(f"{BASE}/9999").status_code == 404
