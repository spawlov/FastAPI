import pytest
from fastapi.testclient import TestClient
from app.main import app, Base, engine

Base.metadata.create_all(bind=engine)
client = TestClient(app)

@pytest.mark.asyncio
async def test_register_user():
    response = client.post(
        "/register", json={"username": "test_user", "email": "test_user@example.com"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "username": "test_user",
        "email": "test_user@example.com",
    }


@pytest.mark.asyncio
async def test_register_user_already_exists():
    client.post(
        "/register",
        json={
            "username": "test_user",
            "email": "test_user@example.com",
        },
    )
    response = client.post(
        "/register",
        json={
            "username": "test_user",
            "email": "test_user@example.com",
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "User already registered"}


@pytest.mark.asyncio
async def test_get_user():
    response = client.get("/user/test_user")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "username": "test_user",
        "email": "test_user@example.com",
    }


@pytest.mark.asyncio
async def test_get_user_not_found():
    response = client.get("/user/someone")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


@pytest.mark.asyncio
async def test_delete_user():
    response = client.delete("/user/test_user")
    assert response.status_code == 200
    assert response.json() == {"detail": "User deleted"}


@pytest.mark.asyncio
async def test_delete_user_not_found():
    response = client.delete("/user/someone")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
