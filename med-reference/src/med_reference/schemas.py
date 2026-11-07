from pydantic import BaseModel, Field


class Condition(BaseModel):
    code: str
    name: str


class SearchRequest(BaseModel):
    query: str
    limit: int = Field(ge=1, le=50, default=10)