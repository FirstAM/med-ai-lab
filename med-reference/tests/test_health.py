from fastapi.testclient import TestClient
from med_reference.main import app

client = TestClient(app)

def test_health() -> None:
    result = client.get("/health")
    assert result.status_code == 200
    assert result.json() == {"status": "ok"}