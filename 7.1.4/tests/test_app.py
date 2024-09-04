from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_calculate_sum():
    response = client.get("/sum?a=5&b=10")
    assert response.status_code == 200
    assert response.json() == {"result": 15}
