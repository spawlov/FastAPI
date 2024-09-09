from typing import Any
from app.main import UserResponse


def test_create_user(client) -> None:
    user_data: dict[str, str] = {"name": "Test User", "email": "test_user@example.com"}
    response: Any = client.post("/create_user/", json=user_data)
    assert response.status_code == 201
    user_response: Any = UserResponse(**response.json())
    assert user_response.name == user_data["name"]
    assert user_response.email == user_data["email"]


def test_create_duplicate_user(client) -> None:
    user_data: dict[str, str] = {
        "name": "Duplicate User",
        "email": "duplicate@example.com",
    }
    response: Any = client.post("/create_user/", json=user_data)
    assert response.status_code == 201
    response: Any = client.post("/create_user/", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "User already registered"


def test_create_user_with_duplicate_email(client) -> None:
    user_data_1: dict[str, str] = {"name": "User One", "email": "unique@example.com"}
    user_data_2: dict[str, str] = {"name": "User Two", "email": "unique@example.com"}
    response: Any = client.post("/create_user/", json=user_data_1)
    assert response.status_code == 201
    response: Any = client.post("/create_user/", json=user_data_2)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_get_user_by_id(client) -> None:
    user_data: dict[str, str] = {"name": "User", "email": "user@example.com"}
    response: Any = client.post("/create_user/", json=user_data)
    assert response.status_code == 201
    response: Any = client.get("/user/1")
    user_response: Any = UserResponse(**response.json())
    assert response.status_code == 200
    assert user_response.id == 1
    assert user_response.name == user_data["name"]
    assert user_response.email == user_data["email"]


def test_get_not_exists_user(client) -> None:
    response: Any = client.get("/user/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_update_user(client) -> None:
    user_data: dict[str, str] = {"name": "User", "email": "user@example.com"}
    response: Any = client.post("/create_user/", json=user_data)
    assert response.status_code == 201
    user_update_data: dict[str, str] = {
        "name": "Updated",
        "email": "updated@example.com",
    }
    response: Any = client.put("/update_user/1", json=user_update_data)
    user_response: Any = UserResponse(**response.json())
    assert response.status_code == 200
    assert user_response.id == 1
    assert user_response.name == user_update_data["name"]
    assert user_response.email == user_update_data["email"]


def test_update_not_exists_user(client) -> None:
    user_data: dict[str, str] = {"name": "User", "email": "user@example.com"}
    response: Any = client.put("/update_user/1", json=user_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_delete_user(client) -> None:
    user_data: dict[str, str] = {"name": "User", "email": "user@example.com"}
    response: Any = client.post("/create_user/", json=user_data)
    assert response.status_code == 201
    response: Any = client.delete("/delete_user/1")
    assert response.status_code == 200
    assert response.json()["detail"] == "User id=1 deleted"


def test_delete_not_exists_user(client) -> None:
    response: Any = client.delete("/delete_user/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
