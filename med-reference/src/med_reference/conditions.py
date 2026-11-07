from fastapi import HTTPException
from fastapi import APIRouter

from med_reference import ols
from med_reference.schemas import Condition
from med_reference.schemas import SearchRequest

router = APIRouter(prefix="/conditions")

CONDITIONS = {}


@router.get("/{code}")
async def get_condition(code) -> Condition:
    condition = await ols.get_by_code(code)
    if condition is None:
        raise HTTPException(status_code=404, detail="Condition not found", )
    else:
        return condition


@router.post("/search")
async def search_conditions(request: SearchRequest) -> list[Condition]:
    result = await ols.search(query=request.query, limit=request.limit)
    return result
