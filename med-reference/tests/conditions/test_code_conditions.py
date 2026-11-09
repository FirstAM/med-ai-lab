from _pytest.monkeypatch import MonkeyPatch

from med_reference import ols
from med_reference.schemas import SearchRequest, Condition


def test_get_by_code(test_client, monkeypatch: MonkeyPatch) -> None:
    code = "MONDO:0004979"
    monkeypatch.setattr(ols, "get_by_code", get_by_code)
    result = test_client.get(f"/conditions/{code}")
    assert result.status_code == 200
    assert result.json() == {"code": "MONDO:0004979", "name": "asthma"}

def test_get_by_code_error(test_client, monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(ols, "get_by_code", get_by_code)
    result = test_client.get("/conditions/MONDO:0004")
    assert result.status_code == 404
    assert result.json() == {"detail": "Condition not found"}


async def get_by_code(code: str) -> Condition| None:
    if code == "MONDO:0004979":
        return Condition(code="MONDO:0004979", name="asthma")
    else:
        return None
