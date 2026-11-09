import pytest
from _pytest.monkeypatch import MonkeyPatch
from httpx2 import HTTPError

from med_reference import ols
from med_reference.schemas import SearchRequest, Condition


def test_get_by_search(test_client, monkeypatch: MonkeyPatch) -> None:
    test_request = SearchRequest(query="asthma", limit=2)
    monkeypatch.setattr(ols, "search", success_stub)
    result = test_client.post("/conditions/search", json=test_request.model_dump(mode="json"))
    assert result.status_code == 200
    assert result.json() == [{"code": "MONDO:0004979", "name": "asthma"}]


def test_error_request_get_by_search(test_client, monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(ols, "search", error_stub)
    result = test_client.post("/conditions/search", json={"query": "asthma", "limit": 0})
    assert result.status_code == 422
    assert [error["loc"] for error in result.json()["detail"]] == [["body", "limit"]]


def test_error_get_by_search(test_client, monkeypatch: MonkeyPatch) -> None:
    test_request = SearchRequest(query="asthma", limit=2)
    monkeypatch.setattr(ols, "search", error_stub)
    result = test_client.post("/conditions/search", json=test_request.model_dump(mode="json"))
    assert result.status_code == 502
    assert result.json() == {"detail":"OLS unavailable ols.search must not be called"}


async def success_stub(query: str, limit: int) -> list[Condition]:
    return [Condition(code="MONDO:0004979", name="asthma")]


async def error_stub(query: str, limit: int) -> list[Condition]:
    raise HTTPError("ols.search must not be called")
