from typing import Any
from unittest import case

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

CONDITIONS = {
    "E11.9": "Type 2 diabetes mellitus without complications",
    "J45.909": "Unspecified asthma, uncomplicated",
    "C50.919": "Malignant neoplasm of unspecified site of unspecified female breast",
}

app = FastAPI()

class Condition(BaseModel):
    code: str
    name: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/conditions/{code}")
async def get_condition(code) -> Condition:
    name = CONDITIONS.get(code)
    if name is None:
        raise HTTPException(status_code=404, detail="Condition not found", )
    else:
        return Condition(code=code, name=name)


class SearchRequest(BaseModel):
    query: str
    limit: int = Field(ge=1, le=50, default=10)


@app.post("/conditions/search")
async def search_conditions(request: SearchRequest) -> list[Condition]:
    response = []
    for code, name in CONDITIONS.items():
        if request.query.lower() in name.lower():
            response.append(Condition(code=code, name=name))

    return response[:request.limit]
