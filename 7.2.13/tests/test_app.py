from typing import Any, Generator
from unittest import TestCase
from unittest.mock import AsyncMock, patch
from fastapi import Response
from fastapi.testclient import TestClient
import pytest

from app.main import app

client = TestClient(app)


@pytest.fixture
def clear_db() -> Generator[None, Any, None]:
    yield
    app.dependency_overrides.clear()


def test_create_item(clear_db) -> None:
    response: Response = client.post("/items/", json={"id": 1, "name": "Item 1"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Item 1"}


def test_create_existing_item(clear_db) -> None:
    client.post("/items/", json={"id": 1, "name": "Item 1"})
    response: Response = client.post("/items/", json={"id": 1, "name": "Item 1"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Item already exists"}


def test_create_wrong_id(clear_db) -> None:
    client.post("/items/", json={"id": "someid", "name": "Some item"})
    response: Response = client.post(
        "/items/", json={"id": "someid", "name": "Some item"}
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": "someid",
                "loc": [
                    "body",
                    "id",
                ],
                "msg": "Input should be a valid integer, unable to parse string as an "
                "integer",
                "type": "int_parsing",
            },
        ],
    }


def test_read_item(clear_db) -> None:
    client.post("/items/", json={"id": 2, "name": "Item 2"})
    response: Response = client.get("/item/2")
    assert response.status_code == 200
    assert response.json() == {"id": 2, "name": "Item 2"}


def test_read_non_existing_item(clear_db) -> None:
    response: Response = client.get("/item/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


class TestApi(TestCase):

    @patch("httpx.AsyncClient.get", new_callable=AsyncMock)
    async def test_get_places(self, mock_get_places) -> None:
        mock_response: list[dict[str, Any]] = [
            {
                "title": "Title 1",
                "imgs": ["img_1_1.jpg", "img_1_2.jpg"],
                "description_short": "Description_short_1",
                "description_long_1": "Description_long_1",
                "coordinates": {"lng": 11.1111, "lat": 11.1111},
            },
            {
                "title": "Title 2",
                "imgs": ["img_2_1.jpg", "img_2_2.jpg"],
                "description_short": "Description_short_2",
                "description_long_1": "Description_long_2",
                "coordinates": {"lng": 22.2222, "lat": 22.2222},
            },
        ]
        mock_get_places.return_value.__aenter__.return_value.status_code = 200
        mock_get_places.return_value.__aenter__.return_value.json.return_value = (
            mock_response
        )

        response: Any = await client.get("/api/places/")

        mock_get_places.assert_called_once()
        mock_get_places.assert_called_once_with(mock_response)

        self.assertEqual(len(mock_get_places.call_args[0]), 0)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), mock_response)

    @patch("httpx.AsyncClient.get", new_callable=AsyncMock)
    async def test_get_place_success(self, mock_get_place) -> None:
        mock_response: list[dict[str, Any]] = [
            {
                "title": "Title 1",
                "imgs": ["img_1_1.jpg", "img_1_2.jpg"],
                "description_short": "Description_short_1",
                "description_long": "Description_long_1",
                "coordinates": {"lng": 11.1111, "lat": 11.1111},
            },
            {
                "title": "Title 2",
                "imgs": ["img_2_1.jpg", "img_2_2.jpg"],
                "description_short": "Description_short_2",
                "description_long": "Description_long_2",
                "coordinates": {"lng": 22.2222, "lat": 22.2222},
            },
        ]
        mock_get_place.return_value.__aenter__.return_value.status_code = 200
        mock_get_place.return_value.__aenter__.return_value.json.return_value = (
            mock_response
        )

        response: Any = await client.get("/api/place/1")

        mock_get_place.assert_called_once()
        mock_get_place.assert_called_once_with(mock_response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), mock_response[1])

    @patch("httpx.AsyncClient.get", new_callable=AsyncMock)
    async def test_get_place_not_found(self, mock_get_place) -> None:
        mock_response: list[dict[str, Any]] = [
            {
                "title": "Title 1",
                "imgs": ["img_1_1.jpg", "img_1_2.jpg"],
                "description_short": "Description_short_1",
                "description_long": "Description_long_1",
                "coordinates": {"lng": 11.1111, "lat": 11.1111},
            }
        ]
        mock_get_place.return_value.__aenter__.return_value.status_code = 200
        mock_get_place.return_value.__aenter__.return_value.json.return_value = (
            mock_response
        )

        response: Any = await client.get("/api/place/1")

        mock_get_place.assert_called_once()
        mock_get_place.assert_called_once_with(mock_response)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Item not found"})

    @patch("httpx.AsyncClient.get", new_callable=AsyncMock)
    async def test_get_place_invalid_id(self, mock_get) -> None:
        response: Any = await client.get("/api/place/-1")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Id mast be positive or 0"})
