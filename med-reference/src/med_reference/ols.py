import httpx2

from med_reference.schemas import Condition

EBI_URL = "https://www.ebi.ac.uk/ols4/api/search"


async def search(query: str, limit: int) -> list[Condition]:
    return await _fetch_conditions({"q": query, "ontology": "mondo", "rows": limit})


async def get_by_code(code: str) -> Condition | None:
    result = await _fetch_conditions(
        {
            "q": code,
            "queryFields": "obo_id",
            "ontology": "mondo",
            "exact": "true",
            "rows": 1,
        }
    )
    if len(result) == 0:
        return None
    else:
        return result[0]


async def _fetch_conditions(params: dict[str, str | int]) -> list[Condition]:
    result = []
    async with httpx2.AsyncClient(timeout=10.0) as client:
        response = await client.get(url=EBI_URL, params=params)
        response.raise_for_status()
        for i in response.json()["response"]["docs"]:
            result.append(Condition(code=i["obo_id"], name=i["label"]))

    return result
