import asyncio
import time
from asyncio import timeout, Timeout
from time import sleep

import httpx2
from med_reference.schemas import Condition

EBI_URL="https://www.ebi.ac.uk/ols4/api/search"


async def _fetch_conditions(params: dict[str, str| int]) -> list[Condition]:
    result = []
    async with httpx2.AsyncClient(timeout = 10.0) as client:
        response = await client.get(url=EBI_URL, params=params)
        for i in response.json()["response"]["docs"]:
            result.append(Condition(
                code=i["obo_id"],
                name=i["label"]
            ))

    return result


async def search(query: str, limit: int) -> list[Condition]:
    start = time.perf_counter()
    sleep(0.5)

    end = time.perf_counter()
    print(f"timer: {end-start}")
    return await _fetch_conditions({"q": query, "ontology": "mondo", "rows": limit})


async def get_by_code(code: str) -> Condition | None:
    result = await _fetch_conditions({"q": code, "queryFields": "obo_id" , "ontology": "mondo", "exact" :"true", "rows": 1}  )
    if len(result) == 0:
        return None
    else:
        return result[0]