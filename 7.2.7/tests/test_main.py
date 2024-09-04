import unittest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)


class TestMain(unittest.TestCase):

    @patch("main.fetch_data_from_api")
    @patch("main.process_data")
    def test_get_and_process_data(self, mock_process_data, mock_fetch_data) -> None:
        # Имитируем функцию fetch_data_from_api, чтобы вернуть пример ответа
        mock_response: dict[str, str] = {"key": "value"}
        mock_fetch_data.return_value = mock_response

        # имитируем функцию process_data
        mock_processed_data: dict[str, str] = {"KEY": "VALUE"}
        mock_process_data.return_value = mock_processed_data

        # отправляем запрос на конечную точку /data/
        response = client.get("/data/")

        # наши assertions
        mock_fetch_data.assert_called_once()  # Убеждаемся, что fetch_data_from_api был вызван один раз
        mock_process_data.assert_called_once_with(
            mock_response
        )  # убеждаемся, что process_data был вызван с "mocked response"
        self.assertEqual(
            response.status_code, 200
        )  # проверяем что status code равен 200
        self.assertEqual(
            response.json(), mock_processed_data
        )  # проверяем, что данные ответа соответствуют имитируемым обработанным данным
