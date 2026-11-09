import asyncio
from typing import Any, Callable

import httpx2
import pytest
from httpx2 import Request, HTTPStatusError

from med_reference import ols
from med_reference.schemas import Condition

RealAsyncClient = httpx2.AsyncClient

def use_mock_ols(monkeypatch: pytest.MonkeyPatch, handler: Any) -> None:
    def make_client(**kwargs: Any) -> httpx2.AsyncClient:
        return RealAsyncClient(transport=httpx2.MockTransport(handler), **kwargs)

    monkeypatch.setattr(httpx2, "AsyncClient", make_client)


@pytest.fixture
def mock_ols(monkeypatch: pytest.MonkeyPatch) -> Callable[[int, Any], list[httpx2.Request]]:
    def install(status: int, body: Any) -> list[httpx2.Request]:
        seen: list[httpx2.Request] = []

        def handler(request: httpx2.Request) -> httpx2.Response:
            seen.append(request)
            return httpx2.Response(status, json=body)

        use_mock_ols(monkeypatch, handler)
        return seen

    return install

def test_ols_code_empty(mock_ols: Callable[[int, Any], list[httpx2.Request]]):
    seen = mock_ols(200, {"response": {"docs": []}})
    result = asyncio.run(ols.get_by_code("MONDO:9999999"))
    assert result is None
    assert seen[0].url.params["q"] == "MONDO:9999999"
    assert seen[0].url.params["queryFields"] == "obo_id"
    assert seen[0].url.params["ontology"] == "mondo"
    assert seen[0].url.params["exact"] == "true"
    assert seen[0].url.params["rows"] == "1"

def test_ols_code(mock_ols: Callable[[int, Any], list[httpx2.Request]]):
    seen = mock_ols(200, {"response": {"docs": [{"obo_id": "MONDO:0004979", "label": "asthma"}]}})
    result = asyncio.run(ols.get_by_code("MONDO:0004979"))
    assert result == Condition(code="MONDO:0004979", name="asthma")
    assert seen[0].url.params["q"] == "MONDO:0004979"
    assert seen[0].url.params["queryFields"] == "obo_id"
    assert seen[0].url.params["ontology"] == "mondo"
    assert seen[0].url.params["exact"] == "true"
    assert seen[0].url.params["rows"] == "1"


def test_ols_search(mock_ols: Callable[[int, Any], list[httpx2.Request]]):
    seen = mock_ols(200, {"response": {"docs": [{"obo_id": "MONDO:0004979", "label": "asthma"}]}})
    result = asyncio.run(ols.search("asthma", 1))
    assert result == [Condition(code="MONDO:0004979", name="asthma")]
    assert seen[0].url.params["q"] == "asthma"
    assert seen[0].url.params["ontology"] == "mondo"
    assert seen[0].url.params["rows"] == "1"


def test_ols_error(mock_ols: Callable[[int, Any], list[httpx2.Request]]):
    seen = mock_ols(500, {})
    with pytest.raises(HTTPStatusError):
        asyncio.run(ols.search("asthma", 1))
    assert seen[0].url.params["q"] == "asthma"
    assert seen[0].url.params["ontology"] == "mondo"
    assert seen[0].url.params["rows"] == "1"