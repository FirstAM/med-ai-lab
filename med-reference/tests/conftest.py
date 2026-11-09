import pytest
from fastapi.testclient import TestClient
from med_reference.main import app


@pytest.fixture
def test_client()-> TestClient:
    return TestClient(app)