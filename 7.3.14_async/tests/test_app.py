import time
import pytest
from httpx import AsyncClient

from app.main import app, UserResponse

@pytest.mark.asyncio
async def test_create_item(client):
    user_data: dict[str, str] = {"name": "Test User", "email": "test@example.com"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/create_user/", json=user_data)

    # assert response.status_code == 200
#     user_response = UserResponse(**response.json())
#     assert user_response.name == user_data["name"]
#     assert user_response.email == user_data["email"]
        
        # response = await ac.post("/items/", json=user_data)
    # time.sleep(30)
    # assert response.status_code == 200
    assert response.json() == {"item1":"blabla"}






































# import os
# import time
# import pytest

# from app.main import UserResponse


# @pytest.mark.asyncio
# async def test_create_user(init_database, client) -> None:
#     user_data: dict[str, str] = {"name": "Test User", "email": "test@example.com"}
#     response = await client.post("/create_user/", json=user_data)

#     assert response.status_code == 200
#     user_response = UserResponse(**response.json())
#     assert user_response.name == user_data["name"]
#     assert user_response.email == user_data["email"]
#     time.sleep(5)


# @pytest.mark.asyncio
# async def test_create_duplicate_user(init_database, client) -> None:
#     user_data: dict[str, str] = {
#         "name": "Duplicate User",
#         "email": "duplicate@example.com",
#     }
#     response = await client.post("/create_user/", json=user_data)

#     assert response.status_code == 200

#     response = await client.post("/create_user/", json=user_data)
#     assert response.status_code == 400
#     assert response.json()["detail"] == "User already registered"
#     time.sleep(5)


# @pytest.mark.asyncio
# async def test_create_user_with_duplicate_email(init_database, client) -> None:
#     user_data_1 = {"name": "User One", "email": "unique@example.com"}
#     user_data_2 = {"name": "User Two", "email": "unique@example.com"}

#     response = await client.post("/create_user/", json=user_data_1)
#     assert response.status_code == 200  # Создаем первого пользователя успешно

#     response = await client.post(
#         "/create_user/", json=user_data_2
#     )  # Пытаемся создать пользователя с тем же email
#     assert response.status_code == 400
#     assert response.json()["detail"] == "Email already registered"
