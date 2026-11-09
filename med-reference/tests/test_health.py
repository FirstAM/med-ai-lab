def test_health(test_client) -> None:
    result = test_client.get("/health")
    assert result.status_code == 200
    assert result.json() == {"status": "ok"}